#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SHTENCO Tier-1 v2 portfolio compression engines.

This module unifies the production ideas preserved across the SHTENCO archive
lineage: SABF-X fast routing, TSC-X byte-plane/spatial transforms, GRAAL-AIS
version deltas, UMC verified expert selection, exact BIP39 token packing,
Gabriel-Horn multiscale residuals, and mature entropy backends.

The production profiles are intentionally different:

* OMNIA SPEED: tiny verified candidate set, optimized for ratio/time score.
* OMNIA BALANCED: deterministic feature gate plus a bounded candidate set.
* OMNIA MAX: exhaustive fixed portfolio, optimized for stored bytes.
* GABRIEL RANDOM-ACCESS: block objective includes expected range inflation.

Every SHTENCO v2 archive carries original size and SHA-256. A candidate is
admitted only after exact decompression and digest verification.
"""
from __future__ import annotations

import collections
from dataclasses import dataclass
import hashlib
import lzma
import math
import struct
import zlib
from typing import Iterable

import brotli
import zstandard as zstd

try:
    from .gabriel_horn_engine import GabrielHornEngine
    from .shtenco_tier1_engines import (
        GRAALIGCTier1Max,
        NexusUMCTier1,
        TSCTier1Spatial,
    )
except ImportError:  # direct execution from compression_lab/
    from gabriel_horn_engine import GabrielHornEngine
    from shtenco_tier1_engines import GRAALIGCTier1Max, NexusUMCTier1, TSCTier1Spatial

try:
    from mnemonic import Mnemonic
except Exception:  # pragma: no cover - optional outside the pinned environment.
    Mnemonic = None

MAGIC = b"ST2\x01"
VERSION = 1
HEADER = struct.Struct(">4sBBQ32s")

ROUTE_RAW = 0
ROUTE_ZSTD1 = 1
ROUTE_ZSTD3 = 2
ROUTE_ZSTD7 = 3
ROUTE_ZSTD12 = 4
ROUTE_ZSTD19 = 5
ROUTE_BROTLI4 = 6
ROUTE_BROTLI9 = 7
ROUTE_BROTLI11 = 8
ROUTE_ZLIB1 = 9
ROUTE_ZLIB9 = 10
ROUTE_LZMA6 = 11
ROUTE_LZMA9 = 12
ROUTE_DELTA1_ZSTD3 = 13
ROUTE_DELTA1_ZSTD12 = 14
ROUTE_DELTA2_ZSTD12 = 15
ROUTE_SHUFFLE2_ZSTD3 = 16
ROUTE_SHUFFLE4_ZSTD3 = 17
ROUTE_SHUFFLE8_ZSTD7 = 18
ROUTE_SHUFFLE16_ZSTD7 = 19
ROUTE_XOR1_ZSTD3 = 20
ROUTE_XOR4_ZSTD3 = 21
ROUTE_XOR16_ZSTD7 = 22
ROUTE_XOR64_ZSTD7 = 23
ROUTE_XOR256_ZSTD12 = 24
ROUTE_XOR1024_ZSTD12 = 25
ROUTE_VERSION512_ZSTD3 = 26
ROUTE_VERSION1024_ZSTD3 = 27
ROUTE_VERSION4096_ZSTD7 = 28
ROUTE_RLE_ZSTD3 = 29
ROUTE_BIP39_ZSTD3 = 30
ROUTE_GABRIEL_BALANCED = 31
ROUTE_GABRIEL_MAX = 32
ROUTE_TIER1_GRAAL = 33
ROUTE_TIER1_NEXUS = 34
ROUTE_TIER1_TSC = 35

_ZC = {
    level: zstd.ZstdCompressor(
        level=level,
        write_checksum=False,
        write_content_size=True,
        write_dict_id=False,
    )
    for level in (1, 3, 7, 12, 19)
}
_ZD = zstd.ZstdDecompressor()
_WORDLIST: list[str] | None = None
_WORD_LOOKUP: dict[str, int] | None = None


@dataclass(frozen=True)
class Features:
    entropy: float
    printable: float
    zero: float
    adjacent: float
    smooth: float
    similar_blocks: float
    atom_repeat: float


@dataclass(frozen=True)
class Candidate:
    route: int
    archive: bytes
    work: int


def _sha(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _pack(route: int, source: bytes, payload: bytes) -> bytes:
    return HEADER.pack(MAGIC, VERSION, route, len(source), _sha(source)) + payload


def _parse(archive: bytes) -> tuple[int, int, bytes, bytes]:
    if len(archive) < HEADER.size:
        raise ValueError("truncated SHTENCO Tier-1 v2 archive")
    magic, version, route, original_size, digest = HEADER.unpack_from(archive)
    if magic != MAGIC or version != VERSION:
        raise ValueError("not a supported SHTENCO Tier-1 v2 archive")
    return route, original_size, digest, archive[HEADER.size:]


def _verify(data: bytes, size: int, digest: bytes) -> bytes:
    if len(data) != size or _sha(data) != digest:
        raise ValueError("SHTENCO Tier-1 v2 size/SHA-256 mismatch")
    return data


def _features(data: bytes) -> Features:
    sample = data[: min(len(data), 8192)]
    n = max(1, len(sample))
    counts = collections.Counter(sample)
    entropy = -sum((count / n) * math.log2(count / n) for count in counts.values())
    printable = sum(value in (9, 10, 13) or 32 <= value < 127 for value in sample) / n
    zero = sample.count(0) / n
    adjacent = sum(sample[i] == sample[i - 1] for i in range(1, len(sample))) / n
    smooth = sum(abs(sample[i] - sample[i - 1]) <= 2 for i in range(1, len(sample))) / n
    similar = 0.0
    half = min(4096, len(data) // 2)
    if half:
        similar = sum(a == b for a, b in zip(data[:half], data[half:half * 2])) / half
    atoms = [sample[i:i + 16] for i in range(0, len(sample) - 15, 16)]
    atom_repeat = 1.0 - len(set(atoms)) / len(atoms) if atoms else 0.0
    return Features(entropy, printable, zero, adjacent, smooth, similar, atom_repeat)


def _delta_encode(data: bytes) -> bytes:
    out = bytearray(len(data))
    previous = 0
    for index, value in enumerate(data):
        out[index] = (value - previous) & 0xFF
        previous = value
    return bytes(out)


def _delta_decode(data: bytes) -> bytes:
    out = bytearray(len(data))
    previous = 0
    for index, value in enumerate(data):
        previous = (previous + value) & 0xFF
        out[index] = previous
    return bytes(out)


def _shuffle_encode(data: bytes, width: int) -> bytes:
    return b"".join(data[offset::width] for offset in range(width))


def _shuffle_decode(data: bytes, width: int) -> bytes:
    n = len(data)
    lengths = [(n - offset + width - 1) // width if offset < n else 0 for offset in range(width)]
    columns: list[bytes] = []
    cursor = 0
    for length in lengths:
        columns.append(data[cursor:cursor + length])
        cursor += length
    if cursor != n:
        raise ValueError("invalid Tier-1 v2 shuffled stream")
    positions = [0] * width
    out = bytearray(n)
    for index in range(n):
        column = index % width
        out[index] = columns[column][positions[column]]
        positions[column] += 1
    return bytes(out)


def _xor_lag_encode(data: bytes, lag: int) -> bytes:
    if lag <= 0 or lag >= len(data):
        return data
    out = bytearray(data)
    for index in range(len(out) - 1, lag - 1, -1):
        out[index] ^= data[index - lag]
    return bytes(out)


def _xor_lag_decode(data: bytes, lag: int) -> bytes:
    if lag <= 0 or lag >= len(data):
        return data
    out = bytearray(data)
    for index in range(lag, len(out)):
        out[index] ^= out[index - lag]
    return bytes(out)


def _version_xor_encode(data: bytes, block_size: int) -> bytes:
    out = bytearray()
    previous = bytes(block_size)
    for start in range(0, len(data), block_size):
        block = data[start:start + block_size]
        out.extend(a ^ b for a, b in zip(block, previous))
        previous = block + bytes(block_size - len(block))
    return bytes(out)


def _version_xor_decode(data: bytes, block_size: int) -> bytes:
    out = bytearray()
    previous = bytes(block_size)
    for start in range(0, len(data), block_size):
        patch = data[start:start + block_size]
        block = bytes(a ^ b for a, b in zip(patch, previous))
        out += block
        previous = block + bytes(block_size - len(block))
    return bytes(out)


def _rle_encode(data: bytes) -> bytes:
    out = bytearray()
    index = 0
    while index < len(data):
        run = 1
        while index + run < len(data) and data[index + run] == data[index] and run < 65535:
            run += 1
        if run >= 4:
            out.append(1)
            out += struct.pack(">H", run)
            out.append(data[index])
            index += run
            continue
        start = index
        index += run
        while index < len(data):
            next_run = 1
            while index + next_run < len(data) and data[index + next_run] == data[index] and next_run < 65535:
                next_run += 1
            if next_run >= 4 or index - start >= 65535:
                break
            index += next_run
        literal = data[start:index]
        out.append(0)
        out += struct.pack(">H", len(literal))
        out += literal
    return bytes(out)


def _rle_decode(data: bytes) -> bytes:
    out = bytearray()
    position = 0
    while position < len(data):
        if position + 3 > len(data):
            raise ValueError("truncated Tier-1 v2 RLE token")
        kind = data[position]
        count = struct.unpack(">H", data[position + 1:position + 3])[0]
        position += 3
        if kind == 1:
            if position >= len(data):
                raise ValueError("truncated Tier-1 v2 RLE run")
            out.extend(bytes([data[position]]) * count)
            position += 1
        elif kind == 0:
            if position + count > len(data):
                raise ValueError("truncated Tier-1 v2 RLE literal")
            out += data[position:position + count]
            position += count
        else:
            raise ValueError("unknown Tier-1 v2 RLE token")
    return bytes(out)


def _pack_11(values: Iterable[int]) -> bytes:
    out = bytearray()
    accumulator = bits = 0
    for value in values:
        accumulator = (accumulator << 11) | (value & 2047)
        bits += 11
        while bits >= 8:
            bits -= 8
            out.append((accumulator >> bits) & 0xFF)
    if bits:
        out.append((accumulator << (8 - bits)) & 0xFF)
    return bytes(out)


def _unpack_11(data: bytes, count: int) -> list[int]:
    result: list[int] = []
    accumulator = bits = 0
    for byte in data:
        accumulator = (accumulator << 8) | byte
        bits += 8
        while bits >= 11 and len(result) < count:
            bits -= 11
            result.append((accumulator >> bits) & 2047)
    if len(result) != count:
        raise ValueError("truncated Tier-1 v2 BIP39 stream")
    return result


def _word_tables() -> tuple[list[str], dict[str, int]]:
    global _WORDLIST, _WORD_LOOKUP
    if Mnemonic is None:
        raise ValueError("BIP39 route requires mnemonic")
    if _WORDLIST is None or _WORD_LOOKUP is None:
        _WORDLIST = Mnemonic("english").wordlist
        _WORD_LOOKUP = {word: index for index, word in enumerate(_WORDLIST)}
    return _WORDLIST, _WORD_LOOKUP


def _bip39_encode(data: bytes) -> bytes | None:
    if Mnemonic is None or not data:
        return None
    try:
        text = data.decode("ascii")
    except UnicodeDecodeError:
        return None
    trailing = len(text) - len(text.rstrip(" "))
    core = text[:-trailing] if trailing else text
    words = core.split(" ") if core else []
    if not words or any(not word for word in words):
        return None
    _, lookup = _word_tables()
    try:
        indices = [lookup[word] for word in words]
    except KeyError:
        return None
    return struct.pack(">IB", len(indices), trailing) + _pack_11(indices)


def _bip39_decode(data: bytes) -> bytes:
    if len(data) < 5:
        raise ValueError("truncated Tier-1 v2 BIP39 header")
    count, trailing = struct.unpack(">IB", data[:5])
    words, _ = _word_tables()
    return (" ".join(words[index] for index in _unpack_11(data[5:], count)) + " " * trailing).encode("ascii")


def _zcompress(data: bytes, level: int) -> bytes:
    return _ZC[level].compress(data)


def _zdecompress(data: bytes, size: int) -> bytes:
    return _ZD.decompress(data, max_output_size=size)


def _encode_route(route: int, source: bytes, gabriel_balanced: GabrielHornEngine, gabriel_max: GabrielHornEngine) -> bytes | None:
    if route == ROUTE_RAW:
        return source
    if route in (ROUTE_ZSTD1, ROUTE_ZSTD3, ROUTE_ZSTD7, ROUTE_ZSTD12, ROUTE_ZSTD19):
        level = {ROUTE_ZSTD1: 1, ROUTE_ZSTD3: 3, ROUTE_ZSTD7: 7, ROUTE_ZSTD12: 12, ROUTE_ZSTD19: 19}[route]
        return _zcompress(source, level)
    if route in (ROUTE_BROTLI4, ROUTE_BROTLI9, ROUTE_BROTLI11):
        quality = {ROUTE_BROTLI4: 4, ROUTE_BROTLI9: 9, ROUTE_BROTLI11: 11}[route]
        return brotli.compress(source, quality=quality)
    if route == ROUTE_ZLIB1:
        return zlib.compress(source, 1)
    if route == ROUTE_ZLIB9:
        return zlib.compress(source, 9)
    if route == ROUTE_LZMA6:
        return lzma.compress(source, preset=6)
    if route == ROUTE_LZMA9:
        return lzma.compress(source, preset=9 | lzma.PRESET_EXTREME)
    if route == ROUTE_DELTA1_ZSTD3:
        return _zcompress(_delta_encode(source), 3)
    if route == ROUTE_DELTA1_ZSTD12:
        return _zcompress(_delta_encode(source), 12)
    if route == ROUTE_DELTA2_ZSTD12:
        return _zcompress(_delta_encode(_delta_encode(source)), 12)
    if route in (ROUTE_SHUFFLE2_ZSTD3, ROUTE_SHUFFLE4_ZSTD3, ROUTE_SHUFFLE8_ZSTD7, ROUTE_SHUFFLE16_ZSTD7):
        width, level = {
            ROUTE_SHUFFLE2_ZSTD3: (2, 3),
            ROUTE_SHUFFLE4_ZSTD3: (4, 3),
            ROUTE_SHUFFLE8_ZSTD7: (8, 7),
            ROUTE_SHUFFLE16_ZSTD7: (16, 7),
        }[route]
        return _zcompress(_shuffle_encode(source, width), level)
    if route in (ROUTE_XOR1_ZSTD3, ROUTE_XOR4_ZSTD3, ROUTE_XOR16_ZSTD7, ROUTE_XOR64_ZSTD7, ROUTE_XOR256_ZSTD12, ROUTE_XOR1024_ZSTD12):
        lag, level = {
            ROUTE_XOR1_ZSTD3: (1, 3),
            ROUTE_XOR4_ZSTD3: (4, 3),
            ROUTE_XOR16_ZSTD7: (16, 7),
            ROUTE_XOR64_ZSTD7: (64, 7),
            ROUTE_XOR256_ZSTD12: (256, 12),
            ROUTE_XOR1024_ZSTD12: (1024, 12),
        }[route]
        return _zcompress(_xor_lag_encode(source, lag), level)
    if route in (ROUTE_VERSION512_ZSTD3, ROUTE_VERSION1024_ZSTD3, ROUTE_VERSION4096_ZSTD7):
        block, level = {
            ROUTE_VERSION512_ZSTD3: (512, 3),
            ROUTE_VERSION1024_ZSTD3: (1024, 3),
            ROUTE_VERSION4096_ZSTD7: (4096, 7),
        }[route]
        return _zcompress(_version_xor_encode(source, block), level)
    if route == ROUTE_RLE_ZSTD3:
        return _zcompress(_rle_encode(source), 3)
    if route == ROUTE_BIP39_ZSTD3:
        encoded = _bip39_encode(source)
        return _zcompress(encoded, 3) if encoded is not None else None
    if route == ROUTE_GABRIEL_BALANCED:
        return gabriel_balanced.compress(source)
    if route == ROUTE_GABRIEL_MAX:
        return gabriel_max.compress(source)
    if route == ROUTE_TIER1_GRAAL:
        return GRAALIGCTier1Max().compress(source)
    if route == ROUTE_TIER1_NEXUS:
        return NexusUMCTier1().compress(source)
    if route == ROUTE_TIER1_TSC:
        return TSCTier1Spatial().compress(source)
    raise ValueError(f"unknown Tier-1 v2 route {route}")


def _decode_route(route: int, payload: bytes, original_size: int, gabriel_balanced: GabrielHornEngine, gabriel_max: GabrielHornEngine) -> bytes:
    if route == ROUTE_RAW:
        return payload
    if route in (ROUTE_ZSTD1, ROUTE_ZSTD3, ROUTE_ZSTD7, ROUTE_ZSTD12, ROUTE_ZSTD19):
        return _zdecompress(payload, original_size)
    if route in (ROUTE_BROTLI4, ROUTE_BROTLI9, ROUTE_BROTLI11):
        return brotli.decompress(payload)
    if route in (ROUTE_ZLIB1, ROUTE_ZLIB9):
        return zlib.decompress(payload)
    if route in (ROUTE_LZMA6, ROUTE_LZMA9):
        return lzma.decompress(payload)
    if route in (ROUTE_DELTA1_ZSTD3, ROUTE_DELTA1_ZSTD12):
        return _delta_decode(_zdecompress(payload, original_size))
    if route == ROUTE_DELTA2_ZSTD12:
        return _delta_decode(_delta_decode(_zdecompress(payload, original_size)))
    if route in (ROUTE_SHUFFLE2_ZSTD3, ROUTE_SHUFFLE4_ZSTD3, ROUTE_SHUFFLE8_ZSTD7, ROUTE_SHUFFLE16_ZSTD7):
        width = {ROUTE_SHUFFLE2_ZSTD3: 2, ROUTE_SHUFFLE4_ZSTD3: 4, ROUTE_SHUFFLE8_ZSTD7: 8, ROUTE_SHUFFLE16_ZSTD7: 16}[route]
        return _shuffle_decode(_zdecompress(payload, original_size), width)
    if route in (ROUTE_XOR1_ZSTD3, ROUTE_XOR4_ZSTD3, ROUTE_XOR16_ZSTD7, ROUTE_XOR64_ZSTD7, ROUTE_XOR256_ZSTD12, ROUTE_XOR1024_ZSTD12):
        lag = {ROUTE_XOR1_ZSTD3: 1, ROUTE_XOR4_ZSTD3: 4, ROUTE_XOR16_ZSTD7: 16, ROUTE_XOR64_ZSTD7: 64, ROUTE_XOR256_ZSTD12: 256, ROUTE_XOR1024_ZSTD12: 1024}[route]
        return _xor_lag_decode(_zdecompress(payload, original_size), lag)
    if route in (ROUTE_VERSION512_ZSTD3, ROUTE_VERSION1024_ZSTD3, ROUTE_VERSION4096_ZSTD7):
        block = {ROUTE_VERSION512_ZSTD3: 512, ROUTE_VERSION1024_ZSTD3: 1024, ROUTE_VERSION4096_ZSTD7: 4096}[route]
        return _version_xor_decode(_zdecompress(payload, original_size), block)
    if route == ROUTE_RLE_ZSTD3:
        return _rle_decode(_ZD.decompress(payload))
    if route == ROUTE_BIP39_ZSTD3:
        return _bip39_decode(_ZD.decompress(payload))
    if route == ROUTE_GABRIEL_BALANCED:
        return gabriel_balanced.decompress(payload)
    if route == ROUTE_GABRIEL_MAX:
        return gabriel_max.decompress(payload)
    if route == ROUTE_TIER1_GRAAL:
        return GRAALIGCTier1Max().decompress(payload)
    if route == ROUTE_TIER1_NEXUS:
        return NexusUMCTier1().decompress(payload)
    if route == ROUTE_TIER1_TSC:
        return TSCTier1Spatial().decompress(payload)
    raise ValueError(f"unknown Tier-1 v2 route {route}")


_WORK = {
    ROUTE_RAW: 0,
    ROUTE_ZSTD1: 1,
    ROUTE_ZSTD3: 2,
    ROUTE_ZSTD7: 5,
    ROUTE_ZSTD12: 9,
    ROUTE_ZSTD19: 15,
    ROUTE_BROTLI4: 4,
    ROUTE_BROTLI9: 12,
    ROUTE_BROTLI11: 24,
    ROUTE_ZLIB1: 2,
    ROUTE_ZLIB9: 10,
    ROUTE_LZMA6: 24,
    ROUTE_LZMA9: 60,
    ROUTE_DELTA1_ZSTD3: 3,
    ROUTE_DELTA1_ZSTD12: 10,
    ROUTE_DELTA2_ZSTD12: 12,
    ROUTE_SHUFFLE2_ZSTD3: 3,
    ROUTE_SHUFFLE4_ZSTD3: 3,
    ROUTE_SHUFFLE8_ZSTD7: 6,
    ROUTE_SHUFFLE16_ZSTD7: 6,
    ROUTE_XOR1_ZSTD3: 3,
    ROUTE_XOR4_ZSTD3: 3,
    ROUTE_XOR16_ZSTD7: 6,
    ROUTE_XOR64_ZSTD7: 6,
    ROUTE_XOR256_ZSTD12: 10,
    ROUTE_XOR1024_ZSTD12: 10,
    ROUTE_VERSION512_ZSTD3: 4,
    ROUTE_VERSION1024_ZSTD3: 4,
    ROUTE_VERSION4096_ZSTD7: 7,
    ROUTE_RLE_ZSTD3: 5,
    ROUTE_BIP39_ZSTD3: 5,
    ROUTE_GABRIEL_BALANCED: 80,
    ROUTE_GABRIEL_MAX: 300,
    ROUTE_TIER1_GRAAL: 18,
    ROUTE_TIER1_NEXUS: 5,
    ROUTE_TIER1_TSC: 8,
}


class _OmniaBase:
    magic = MAGIC
    family = "SHTENCO-OMNIA-TIER1-V2"
    work_weight = 0.0

    def __init__(self) -> None:
        self._gabriel_balanced = GabrielHornEngine(profile="balanced", surface_weight=0.25, work_weight=0.25, entropy_level=7)
        self._gabriel_max = GabrielHornEngine(profile="max", entropy_level=12)
        self.last_mode = "uninitialized"

    def route_ids(self, source: bytes, features: Features) -> list[int]:
        raise NotImplementedError

    def _candidate(self, route: int, source: bytes) -> Candidate | None:
        try:
            payload = _encode_route(route, source, self._gabriel_balanced, self._gabriel_max)
            if payload is None:
                return None
            archive = _pack(route, source, payload)
            restored = _decode_route(route, payload, len(source), self._gabriel_balanced, self._gabriel_max)
            if restored != source or _sha(restored) != _sha(source):
                raise ValueError(f"route {route} failed exact verification")
            return Candidate(route, archive, _WORK[route])
        except Exception:
            return None

    def compress(self, source: bytes) -> bytes:
        source = bytes(source)
        features = _features(source)
        candidates = [item for route in dict.fromkeys(self.route_ids(source, features)) if (item := self._candidate(route, source)) is not None]
        raw = self._candidate(ROUTE_RAW, source)
        if raw is not None and all(item.route != ROUTE_RAW for item in candidates):
            candidates.append(raw)
        if not candidates:
            raise RuntimeError(f"{self.name} found no verified route")
        best = min(candidates, key=lambda item: (len(item.archive) + self.work_weight * item.work, len(item.archive), item.work, item.route))
        self.last_mode = str(best.route)
        if self.decompress(best.archive) != source:
            raise ValueError(f"{self.name} final verification failed")
        return best.archive

    def decompress(self, archive: bytes) -> bytes:
        route, original_size, digest, payload = _parse(archive)
        result = _decode_route(route, payload, original_size, self._gabriel_balanced, self._gabriel_max)
        return _verify(result, original_size, digest)


class OmniaTier1Speed(_OmniaBase):
    name = "SHTENCO OMNIA TIER1 V2 SPEED"
    work_weight = 8.0

    def route_ids(self, source: bytes, features: Features) -> list[int]:
        routes = [ROUTE_RAW, ROUTE_ZSTD1, ROUTE_ZSTD3]
        if features.entropy > 7.90:
            return routes
        if features.smooth > 0.40:
            routes.append(ROUTE_DELTA1_ZSTD3)
        elif features.zero > 0.08:
            routes.append(ROUTE_SHUFFLE4_ZSTD3)
        elif features.similar_blocks > 0.55:
            routes.append(ROUTE_VERSION1024_ZSTD3)
        return routes


class OmniaTier1Balanced(_OmniaBase):
    name = "SHTENCO OMNIA TIER1 V2 BALANCED"
    work_weight = 1.5

    def route_ids(self, source: bytes, features: Features) -> list[int]:
        routes = [ROUTE_RAW, ROUTE_ZSTD1, ROUTE_ZSTD3, ROUTE_ZSTD7]
        if features.printable > 0.72:
            routes += [ROUTE_BROTLI4, ROUTE_BROTLI9]
        if features.smooth > 0.28:
            routes += [ROUTE_DELTA1_ZSTD3, ROUTE_DELTA1_ZSTD12, ROUTE_SHUFFLE4_ZSTD3, ROUTE_SHUFFLE8_ZSTD7]
        if features.zero > 0.05:
            routes += [ROUTE_SHUFFLE4_ZSTD3, ROUTE_SHUFFLE8_ZSTD7, ROUTE_RLE_ZSTD3]
        if features.similar_blocks > 0.35 or features.atom_repeat > 0.18:
            routes += [ROUTE_VERSION512_ZSTD3, ROUTE_VERSION1024_ZSTD3, ROUTE_XOR256_ZSTD12]
        if features.printable > 0.98:
            routes.append(ROUTE_BIP39_ZSTD3)
        if (features.smooth > 0.45 or features.similar_blocks > 0.65) and len(source) <= 131072:
            routes.append(ROUTE_GABRIEL_BALANCED)
        routes += [ROUTE_TIER1_NEXUS]
        return routes


class OmniaTier1Max(_OmniaBase):
    name = "SHTENCO OMNIA TIER1 V2 MAX"
    work_weight = 0.0

    def route_ids(self, source: bytes, features: Features) -> list[int]:
        routes = list(range(ROUTE_RAW, ROUTE_BIP39_ZSTD3 + 1))
        routes += [ROUTE_TIER1_GRAAL, ROUTE_TIER1_NEXUS, ROUTE_TIER1_TSC]
        if len(source) <= 131072:
            routes += [ROUTE_GABRIEL_BALANCED, ROUTE_GABRIEL_MAX]
        return routes


class GabrielHornSpeedTier1(GabrielHornEngine):
    name = "SHTENCO GABRIEL-HORN TIER1 SPEED"
    family = "SHTENCO-GABRIEL"

    def __init__(self) -> None:
        super().__init__(profile="speed", surface_weight=0.5, work_weight=1.0, entropy_level=3)


class GabrielHornBalancedTier1(GabrielHornEngine):
    name = "SHTENCO GABRIEL-HORN TIER1 BALANCED"
    family = "SHTENCO-GABRIEL"

    def __init__(self) -> None:
        super().__init__(profile="balanced", surface_weight=0.5, work_weight=0.5, entropy_level=7)


class GabrielHornRandomAccessTier1(GabrielHornEngine):
    """Gabriel profile with explicit expected range-inflation penalty."""

    name = "SHTENCO GABRIEL-HORN TIER1 RANDOM-ACCESS"
    family = "SHTENCO-GABRIEL"

    def __init__(self, expected_range_bytes: int = 512, access_weight: float = 96.0) -> None:
        super().__init__(profile="balanced", surface_weight=0.5, work_weight=0.5, entropy_level=7)
        self.expected_range_bytes = max(1, int(expected_range_bytes))
        self.access_weight = max(0.0, float(access_weight))

    def compress(self, source: bytes) -> bytes:
        source = bytes(source)
        if not source:
            archive, _ = self._build_archive(source, 1)
            return archive
        sizes = [size for size in (256, 512, 1024, 2048, 4096) if size < len(source)]
        sizes.append(min(len(source), 4096))
        candidates = []
        for size in sorted(set(sizes)):
            archive, cost = self._build_archive(source, size)
            amplification = max(1.0, size / self.expected_range_bytes)
            objective = len(archive) + self.access_weight * amplification + 0.25 * cost.active_shells + 0.25 * cost.transform_work
            candidates.append((objective, len(archive), size, archive))
        _, _, _, archive = min(candidates)
        if self.decompress(archive) != source:
            raise ValueError("Gabriel random-access final verification failed")
        return archive


def tier1_v2_engine_suite() -> list[tuple[str, str, object]]:
    engines = [
        OmniaTier1Speed(),
        OmniaTier1Balanced(),
        OmniaTier1Max(),
        GabrielHornSpeedTier1(),
        GabrielHornBalancedTier1(),
        GabrielHornRandomAccessTier1(),
    ]
    return [(engine.name, getattr(engine, "family", "SHTENCO-TIER1-V2"), engine) for engine in engines]
