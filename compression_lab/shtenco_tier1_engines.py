#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SHTENCO Tier-1 compression engines.

Consolidates SABF-X, EGD-256/GRAAL graph modelling, TSC-X spatial transforms,
GRAAL-AIS version storage, BIP39 engines and NEXUS/UMC routing. Standard entropy
coding remains explicitly Zstandard; SHTENCO technology is the compact binary
container, reversible transforms, graph/version modelling and expert routing.
Every archive contains original size and a full SHA-256 digest.
"""
from __future__ import annotations

import collections
import hashlib
import math
import struct
from typing import Iterable

import zstandard as zstd

try:
    from mnemonic import Mnemonic
except Exception:
    Mnemonic = None

MAGIC = b"ST1\x01"
HEADER = struct.Struct(">4sBI32s")
BLOCK = 1024
_ZC = {level: zstd.ZstdCompressor(level=level, write_checksum=False,
                                  write_content_size=True, write_dict_id=False)
       for level in (1, 2, 3, 5, 7, 12, 19)}
_ZD = zstd.ZstdDecompressor()


def _sha(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _pack(mode: int, source: bytes, payload: bytes) -> bytes:
    return HEADER.pack(MAGIC, mode, len(source), _sha(source)) + payload


def _unpack(archive: bytes) -> tuple[int, int, bytes, bytes]:
    if len(archive) < HEADER.size:
        raise ValueError("truncated Tier-1 archive")
    magic, mode, original_size, digest = HEADER.unpack_from(archive)
    if magic != MAGIC:
        raise ValueError("not a SHTENCO Tier-1 archive")
    return mode, original_size, digest, archive[HEADER.size:]


def _verify(data: bytes, size: int, digest: bytes) -> bytes:
    if len(data) != size or _sha(data) != digest:
        raise ValueError("Tier-1 size/SHA-256 mismatch")
    return data


def _zcompress(data: bytes, level: int) -> bytes:
    return _ZC[level].compress(data)


def _delta_encode(data: bytes) -> bytes:
    if not data:
        return data
    out = bytearray(len(data)); previous = 0
    for i, value in enumerate(data):
        out[i] = (value - previous) & 255; previous = value
    return bytes(out)


def _delta_decode(data: bytes) -> bytes:
    out = bytearray(len(data)); previous = 0
    for i, value in enumerate(data):
        previous = (previous + value) & 255; out[i] = previous
    return bytes(out)


def _plane4_encode(data: bytes) -> bytes:
    pad = (-len(data)) & 3
    padded = data + b"\0" * pad
    return bytes([pad]) + padded[0::4] + padded[1::4] + padded[2::4] + padded[3::4]


def _plane4_decode(data: bytes, original_size: int) -> bytes:
    if not data:
        raise ValueError("truncated byte-plane transform")
    pad, body = data[0], data[1:]
    if pad > 3 or len(body) % 4:
        raise ValueError("invalid byte-plane transform")
    n = len(body) // 4
    out = bytearray(n * 4)
    out[0::4], out[1::4], out[2::4], out[3::4] = body[:n], body[n:2*n], body[2*n:3*n], body[3*n:]
    if len(out) - pad != original_size:
        raise ValueError("byte-plane length mismatch")
    return bytes(out[:original_size])


def _version_xor_encode(data: bytes, block_size: int = BLOCK) -> bytes:
    out = bytearray(); previous = bytes(block_size)
    for start in range(0, len(data), block_size):
        block = data[start:start + block_size]
        out.extend(a ^ b for a, b in zip(block, previous))
        previous = block + bytes(block_size - len(block))
    return bytes(out)


def _version_xor_decode(data: bytes, block_size: int = BLOCK) -> bytes:
    out = bytearray(); previous = bytes(block_size)
    for start in range(0, len(data), block_size):
        patch = data[start:start + block_size]
        block = bytes(a ^ b for a, b in zip(patch, previous))
        out += block; previous = block + bytes(block_size - len(block))
    return bytes(out)


def _sample_features(data: bytes) -> dict[str, float]:
    sample = data[:2048]; n = max(1, len(sample)); counts = collections.Counter(sample)
    entropy = -sum((c/n) * math.log2(c/n) for c in counts.values())
    printable = sum(b in (9,10,13) or 32 <= b < 127 for b in sample) / n
    zero = sample.count(0) / n
    adjacent = sum(sample[i] == sample[i-1] for i in range(1, len(sample))) / n
    smooth = sum(abs(sample[i] - sample[i-1]) <= 2 for i in range(1, len(sample))) / n
    similar = 0.0
    if len(data) >= 2048:
        similar = sum(x == y for x, y in zip(data[:1024], data[1024:2048])) / 1024.0
    return {"entropy": entropy, "printable": printable, "zero": zero,
            "adjacent": adjacent, "smooth": smooth, "similar_blocks": similar}


def _pack_11(values: Iterable[int]) -> bytes:
    out = bytearray(); acc = bits = 0
    for value in values:
        acc = (acc << 11) | (value & 2047); bits += 11
        while bits >= 8:
            bits -= 8; out.append((acc >> bits) & 255)
    if bits: out.append((acc << (8 - bits)) & 255)
    return bytes(out)


def _unpack_11(data: bytes, count: int) -> list[int]:
    result = []; acc = bits = 0
    for byte in data:
        acc = (acc << 8) | byte; bits += 8
        while bits >= 11 and len(result) < count:
            bits -= 11; result.append((acc >> bits) & 2047)
    if len(result) != count: raise ValueError("truncated BIP39 stream")
    return result


def _bip39_encode(data: bytes) -> bytes | None:
    if Mnemonic is None or not data: return None
    sample = data[:512]
    if any(b not in b"abcdefghijklmnopqrstuvwxyz " for b in sample): return None
    try: text = data.decode("ascii")
    except UnicodeDecodeError: return None
    trailing = len(text) - len(text.rstrip(" ")); core = text[:-trailing] if trailing else text
    words = core.split(" ") if core else []
    if not words or any(not word for word in words): return None
    wordlist = Mnemonic("english").wordlist; lookup = {word: i for i, word in enumerate(wordlist)}
    try: indices = [lookup[word] for word in words]
    except KeyError: return None
    return struct.pack(">IB", len(indices), trailing) + _pack_11(indices)


def _bip39_decode(data: bytes) -> bytes:
    if Mnemonic is None or len(data) < 5: raise ValueError("BIP39 unavailable")
    count, trailing = struct.unpack(">IB", data[:5]); words = Mnemonic("english").wordlist
    return (" ".join(words[i] for i in _unpack_11(data[5:], count)) + " " * trailing).encode("ascii")


def _decode_mode(mode: int, payload: bytes, original_size: int) -> bytes:
    if mode == 7: return payload
    transformed = _ZD.decompress(payload)
    if mode in (0,1,2): return transformed
    if mode == 3: return _delta_decode(transformed)
    if mode == 4: return _plane4_decode(transformed, original_size)
    if mode == 5: return _version_xor_decode(transformed)
    if mode == 6: return _bip39_decode(transformed)
    raise ValueError("unknown Tier-1 mode")


class _BaseTier1:
    def decompress(self, archive: bytes) -> bytes:
        mode, size, digest, payload = _unpack(archive)
        return _verify(_decode_mode(mode, payload, size), size, digest)
    @staticmethod
    def _candidate(source: bytes, mode: int, transformed: bytes, level: int) -> bytes:
        return _pack(mode, source, _zcompress(transformed, level))
    def _checked(self, source: bytes, candidates: list[bytes]) -> bytes:
        result = min(candidates + [_pack(7, source, source)], key=len)
        if self.decompress(result) != source: raise ValueError(f"{self.name} verification failed")
        return result


class SABFXTier1Speed(_BaseTier1):
    name = "SHTENCO SABF-X TIER1 SPEED"
    def compress(self, source: bytes) -> bytes:
        return self._checked(source, [self._candidate(source, 0, source, 1)])


class SABFXTier1Balanced(_BaseTier1):
    name = "SHTENCO SABF-X TIER1 BALANCED"
    def compress(self, source: bytes) -> bytes:
        f = _sample_features(source)
        if f["entropy"] > 7.80: mode, transformed, level = 0, source, 1
        elif f["printable"] > .72 or f["adjacent"] > .08: mode, transformed, level = 1, source, 3
        elif f["smooth"] > .45: mode, transformed, level = 3, _delta_encode(source), 3
        elif f["zero"] > .12: mode, transformed, level = 4, _plane4_encode(source), 3
        else: mode, transformed, level = 0, source, 1
        return self._checked(source, [self._candidate(source, mode, transformed, level)])


class TSCTier1Spatial(_BaseTier1):
    name = "SHTENCO TSC-X TIER1 SPATIAL"
    def compress(self, source: bytes) -> bytes:
        return self._checked(source, [self._candidate(source,0,source,1),
            self._candidate(source,3,_delta_encode(source),3),
            self._candidate(source,4,_plane4_encode(source),3)])


class GRAALAISTier1(_BaseTier1):
    name = "SHTENCO GRAAL-AIS TIER1"
    def compress(self, source: bytes) -> bytes:
        f = _sample_features(source)
        if f["similar_blocks"] > .70 and len(source) >= 2048: mode, transformed = 5, _version_xor_encode(source)
        elif f["zero"] > .10: mode, transformed = 4, _plane4_encode(source)
        elif f["smooth"] > .42: mode, transformed = 3, _delta_encode(source)
        else: mode, transformed = 0, source
        return self._checked(source, [self._candidate(source,mode,transformed,1)])


class PBM39Tier1(_BaseTier1):
    name = "SHTENCO PBM-39X TIER1"
    def compress(self, source: bytes) -> bytes:
        transformed = _bip39_encode(source)
        candidate = self._candidate(source,6,transformed,3) if transformed is not None else self._candidate(source,0,source,1)
        return self._checked(source, [candidate])


class GRAALIGCTier1Max(_BaseTier1):
    name = "SHTENCO GRAAL-IGC TIER1 MAX"
    def compress(self, source: bytes) -> bytes:
        candidates = [self._candidate(source,0,source,1), self._candidate(source,1,source,3),
            self._candidate(source,2,source,7), self._candidate(source,3,_delta_encode(source),3),
            self._candidate(source,4,_plane4_encode(source),3), self._candidate(source,5,_version_xor_encode(source),3)]
        mnemonic = _bip39_encode(source)
        if mnemonic is not None: candidates.append(self._candidate(source,6,mnemonic,3))
        return self._checked(source, candidates)


class NexusUMCTier1(_BaseTier1):
    name = "SHTENCO NEXUS-UMC TIER1"
    def compress(self, source: bytes) -> bytes:
        f = _sample_features(source)
        if f["similar_blocks"] > .70: preferred = self._candidate(source,5,_version_xor_encode(source),3)
        else:
            mnemonic = _bip39_encode(source) if f["printable"] > .96 else None
            if mnemonic is not None: preferred = self._candidate(source,6,mnemonic,3)
            elif f["smooth"] > .45: preferred = self._candidate(source,3,_delta_encode(source),3)
            elif f["zero"] > .10: preferred = self._candidate(source,4,_plane4_encode(source),3)
            else: preferred = self._candidate(source,0,source,1)
        return self._checked(source, [preferred, self._candidate(source,0,source,1)])


def tier1_engine_suite() -> list[tuple[str, str, object]]:
    engines = [SABFXTier1Speed(), SABFXTier1Balanced(), GRAALAISTier1(),
               TSCTier1Spatial(), PBM39Tier1(), NexusUMCTier1(), GRAALIGCTier1Max()]
    return [(engine.name, "SHTENCO-TIER1", engine) for engine in engines]
