#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SHTENCO Gabriel Horn lossless compression engine.

The codec turns the Gabriel's-horn analogy into an engineering objective:
minimise finite stored volume while also minimising the decoding/access surface.
It is a block codec with reversible multi-scale transforms, significance shells,
exact deduplication, a random-access index and SHA-256 verification.

No information-theoretic impossibility is bypassed: incompressible input is stored
verbatim. The "horn" is the progressive organization of structured residuals,
not a claim that finite bytes contain arbitrary infinite information.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
import struct
import zlib
from typing import Iterator

try:
    import zstandard as zstd
except Exception:  # pragma: no cover - minimal Python installations.
    zstd = None

MAGIC = b"SGH1"
VERSION = 1
HEADER = struct.Struct(">4sBQII32s")
INDEX_ENTRY = struct.Struct(">QI")

MODE_RAW = 0
MODE_ENTROPY = 1
MODE_SHELLS = 2
MODE_REFERENCE = 3

TRANSFORM_IDENTITY = 0
TRANSFORM_DELTA1 = 1
TRANSFORM_DELTA2 = 2
TRANSFORM_XOR_LAG = 3
TRANSFORM_SHUFFLE = 4
TRANSFORM_HORN_LIFT = 5

CODEC_ZSTD = 1
CODEC_ZLIB = 2

SHELL_ZERO = 0
SHELL_ONE = 1
SHELL_RAW = 2
SHELL_RLE = 3
SHELL_ZSTD = 4
SHELL_ZLIB = 5


@dataclass(frozen=True)
class GabrielCost:
    """Two-axis cost: finite archive volume and decoding surface."""

    volume_bytes: int
    active_shells: int
    transform_work: int
    dependency_depth: int = 0

    def key(self, surface_weight: float, work_weight: float) -> tuple[float, int, int, int]:
        objective = (
            self.volume_bytes
            + surface_weight * self.active_shells
            + work_weight * self.transform_work
            + surface_weight * self.dependency_depth
        )
        return objective, self.volume_bytes, self.active_shells, self.transform_work


@dataclass(frozen=True)
class _RecordCandidate:
    record: bytes
    cost: GabrielCost


@dataclass(frozen=True)
class ArchiveInfo:
    original_size: int
    block_size: int
    block_count: int
    archive_size: int
    raw_blocks: int
    entropy_blocks: int
    shell_blocks: int
    reference_blocks: int
    active_shells: int
    ratio: float


def _sha(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _uvarint(value: int) -> bytes:
    if value < 0:
        raise ValueError("uvarint cannot encode a negative value")
    out = bytearray()
    while value >= 0x80:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value)
    return bytes(out)


def _read_uvarint(data: bytes, offset: int = 0) -> tuple[int, int]:
    value = 0
    shift = 0
    for _ in range(10):
        if offset >= len(data):
            raise ValueError("truncated uvarint")
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value, offset
        shift += 7
    raise ValueError("uvarint is too large")


def _delta_encode(data: bytes) -> bytes:
    out = bytearray(len(data))
    previous = 0
    for i, value in enumerate(data):
        out[i] = (value - previous) & 0xFF
        previous = value
    return bytes(out)


def _delta_decode(data: bytes) -> bytes:
    out = bytearray(len(data))
    previous = 0
    for i, value in enumerate(data):
        previous = (previous + value) & 0xFF
        out[i] = previous
    return bytes(out)


def _xor_lag_encode(data: bytes, lag: int) -> bytes:
    if lag <= 0 or lag >= len(data):
        return data
    out = bytearray(data)
    for i in range(len(data) - 1, lag - 1, -1):
        out[i] ^= data[i - lag]
    return bytes(out)


def _xor_lag_decode(data: bytes, lag: int) -> bytes:
    if lag <= 0 or lag >= len(data):
        return data
    out = bytearray(data)
    for i in range(lag, len(out)):
        out[i] ^= out[i - lag]
    return bytes(out)


def _shuffle_encode(data: bytes, width: int) -> bytes:
    if width <= 1:
        return data
    return b"".join(data[offset::width] for offset in range(width))


def _shuffle_decode(data: bytes, width: int) -> bytes:
    if width <= 1:
        return data
    n = len(data)
    lengths = [(n - offset + width - 1) // width if offset < n else 0 for offset in range(width)]
    columns: list[bytes] = []
    cursor = 0
    for length in lengths:
        columns.append(data[cursor:cursor + length])
        cursor += length
    if cursor != n:
        raise ValueError("invalid shuffled block")
    positions = [0] * width
    out = bytearray(n)
    for i in range(n):
        column = i % width
        out[i] = columns[column][positions[column]]
        positions[column] += 1
    return bytes(out)


def _horn_scales(length: int, levels: int) -> list[int]:
    scales: list[int] = []
    scale = 1
    while scale < length and len(scales) < levels:
        scales.append(scale)
        scale <<= 1
    return scales


def _horn_lift_encode(data: bytes, levels: int) -> bytes:
    """Reversible dyadic modular lifting: coarse core plus residual surface."""
    out = bytearray(data)
    for scale in _horn_scales(len(out), levels):
        for i in range(len(out) - 1, scale - 1, -1):
            out[i] = (out[i] - out[i - scale]) & 0xFF
    return bytes(out)


def _horn_lift_decode(data: bytes, levels: int) -> bytes:
    out = bytearray(data)
    for scale in reversed(_horn_scales(len(out), levels)):
        for i in range(scale, len(out)):
            out[i] = (out[i] + out[i - scale]) & 0xFF
    return bytes(out)


def _apply_transform(data: bytes, transform: int, parameter: int) -> bytes:
    if transform == TRANSFORM_IDENTITY:
        return data
    if transform == TRANSFORM_DELTA1:
        return _delta_encode(data)
    if transform == TRANSFORM_DELTA2:
        return _delta_encode(_delta_encode(data))
    if transform == TRANSFORM_XOR_LAG:
        return _xor_lag_encode(data, parameter)
    if transform == TRANSFORM_SHUFFLE:
        return _shuffle_encode(data, parameter)
    if transform == TRANSFORM_HORN_LIFT:
        return _horn_lift_encode(data, parameter)
    raise ValueError("unknown Gabriel transform")


def _invert_transform(data: bytes, transform: int, parameter: int) -> bytes:
    if transform == TRANSFORM_IDENTITY:
        return data
    if transform == TRANSFORM_DELTA1:
        return _delta_decode(data)
    if transform == TRANSFORM_DELTA2:
        return _delta_decode(_delta_decode(data))
    if transform == TRANSFORM_XOR_LAG:
        return _xor_lag_decode(data, parameter)
    if transform == TRANSFORM_SHUFFLE:
        return _shuffle_decode(data, parameter)
    if transform == TRANSFORM_HORN_LIFT:
        return _horn_lift_decode(data, parameter)
    raise ValueError("unknown Gabriel transform")


def _rle_encode(data: bytes) -> bytes:
    if not data:
        return b""
    out = bytearray()
    start = 0
    while start < len(data):
        value = data[start]
        end = start + 1
        while end < len(data) and data[end] == value:
            end += 1
        out += _uvarint(end - start)
        out.append(value)
        start = end
    return bytes(out)


def _rle_decode(data: bytes, expected_size: int) -> bytes:
    out = bytearray()
    offset = 0
    while offset < len(data):
        count, offset = _read_uvarint(data, offset)
        if count <= 0 or offset >= len(data):
            raise ValueError("invalid Gabriel RLE stream")
        value = data[offset]
        offset += 1
        if len(out) + count > expected_size:
            raise ValueError("Gabriel RLE expands past expected size")
        out.extend([value] * count)
    if len(out) != expected_size:
        raise ValueError("Gabriel RLE size mismatch")
    return bytes(out)


def _entropy_candidates(data: bytes, level: int) -> Iterator[tuple[int, bytes]]:
    yield CODEC_ZLIB, zlib.compress(data, level=min(9, max(1, level)))
    if zstd is not None:
        compressor = zstd.ZstdCompressor(
            level=max(1, min(19, level)),
            write_checksum=False,
            write_content_size=True,
            write_dict_id=False,
        )
        yield CODEC_ZSTD, compressor.compress(data)


def _entropy_decode(codec: int, payload: bytes, expected_size: int) -> bytes:
    if codec == CODEC_ZLIB:
        result = zlib.decompress(payload)
    elif codec == CODEC_ZSTD:
        if zstd is None:
            raise ValueError("archive requires the zstandard package")
        result = zstd.ZstdDecompressor().decompress(payload, max_output_size=expected_size)
    else:
        raise ValueError("unknown Gabriel entropy codec")
    if len(result) != expected_size:
        raise ValueError("Gabriel entropy payload size mismatch")
    return result


def _pack_bitplane(data: bytes, bit: int) -> bytes:
    out = bytearray((len(data) + 7) // 8)
    mask = 1 << bit
    for i, value in enumerate(data):
        if value & mask:
            out[i >> 3] |= 1 << (7 - (i & 7))
    return bytes(out)


def _shell_candidate(plane: bytes, entropy_level: int) -> tuple[int, bytes]:
    candidates: list[tuple[int, bytes]] = [(SHELL_RAW, plane), (SHELL_RLE, _rle_encode(plane))]
    for codec, payload in _entropy_candidates(plane, entropy_level):
        candidates.append((SHELL_ZSTD if codec == CODEC_ZSTD else SHELL_ZLIB, payload))
    return min(candidates, key=lambda item: (1 + len(_uvarint(len(item[1]))) + len(item[1]), item[0]))


def _encode_shells(data: bytes, entropy_level: int) -> tuple[bytes, int]:
    """Encode eight significance shells, most significant first."""
    out = bytearray([8])
    active = 0
    for bit in range(7, -1, -1):
        mask = 1 << bit
        has_zero = any((value & mask) == 0 for value in data)
        has_one = any((value & mask) != 0 for value in data)
        if not has_one:
            out.append(SHELL_ZERO)
            continue
        if not has_zero:
            out.append(SHELL_ONE)
            active += 1
            continue
        plane = _pack_bitplane(data, bit)
        encoding, payload = _shell_candidate(plane, entropy_level)
        out.append(encoding)
        out += _uvarint(len(payload))
        out += payload
        active += 1
    return bytes(out), active


def _decode_shells(payload: bytes, output_size: int, precision_bits: int = 8) -> bytes:
    if not payload or payload[0] != 8:
        raise ValueError("invalid Gabriel shell payload")
    precision_bits = max(0, min(8, precision_bits))
    out = bytearray(output_size)
    plane_size = (output_size + 7) // 8
    offset = 1
    for shell_index, bit in enumerate(range(7, -1, -1)):
        if offset >= len(payload):
            raise ValueError("truncated Gabriel shell descriptor")
        encoding = payload[offset]
        offset += 1
        plane: bytes | None = None
        if encoding in (SHELL_RAW, SHELL_RLE, SHELL_ZSTD, SHELL_ZLIB):
            length, offset = _read_uvarint(payload, offset)
            end = offset + length
            if end > len(payload):
                raise ValueError("truncated Gabriel shell")
            encoded = payload[offset:end]
            offset = end
            if encoding == SHELL_RAW:
                plane = encoded
            elif encoding == SHELL_RLE:
                plane = _rle_decode(encoded, plane_size)
            elif encoding == SHELL_ZSTD:
                plane = _entropy_decode(CODEC_ZSTD, encoded, plane_size)
            else:
                plane = _entropy_decode(CODEC_ZLIB, encoded, plane_size)
            if len(plane) != plane_size:
                raise ValueError("Gabriel shell size mismatch")
        elif encoding not in (SHELL_ZERO, SHELL_ONE):
            raise ValueError("unknown Gabriel shell encoding")

        if shell_index >= precision_bits or encoding == SHELL_ZERO:
            continue
        mask = 1 << bit
        if encoding == SHELL_ONE:
            for i in range(output_size):
                out[i] |= mask
        else:
            assert plane is not None
            for i in range(output_size):
                if plane[i >> 3] & (1 << (7 - (i & 7))):
                    out[i] |= mask
    if offset != len(payload):
        raise ValueError("trailing bytes in Gabriel shell payload")
    return bytes(out)


def _transform_specs(length: int, profile: str) -> list[tuple[int, int, int]]:
    """Return (transform, parameter, rough work units)."""
    specs = [(TRANSFORM_IDENTITY, 0, 0), (TRANSFORM_DELTA1, 0, 1)]
    if profile != "speed":
        specs.append((TRANSFORM_DELTA2, 0, 2))
        for lag in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024):
            if lag < length:
                specs.append((TRANSFORM_XOR_LAG, lag, 1))
        for width in (2, 4, 8, 16):
            if width <= length:
                specs.append((TRANSFORM_SHUFFLE, width, 1))
    max_levels = max(0, int(math.ceil(math.log2(max(1, length)))))
    levels = (1, 2, 4, max_levels) if profile == "max" else (1, min(3, max_levels))
    for level in dict.fromkeys(levels):
        if level > 0:
            specs.append((TRANSFORM_HORN_LIFT, level, level))
    return specs


def _block_sizes(length: int, profile: str) -> list[int]:
    if length <= 0:
        return [1]
    if profile == "speed":
        return [min(16384, max(1024, 1 << max(0, (length - 1).bit_length() - 2)))]
    base = [1024, 4096, 16384] if profile == "balanced" else [256, 512, 1024, 2048, 4096, 8192, 16384, 32768]
    selected = [size for size in base if size < length]
    selected.append(length if length <= 32768 else 32768)
    return sorted(set(max(1, size) for size in selected))


class GabrielHornEngine:
    """Maximum-strength lossless Gabriel Horn codec.

    ``surface_weight`` is measured in virtual bytes. Zero means pure smallest
    archive; a small positive value prefers fewer shells/dependencies when byte
    sizes are close. ``work_weight`` similarly regularises expensive transforms.
    """

    name = "SHTENCO GABRIEL-HORN TIER1 MAX"
    family = "SHTENCO-GABRIEL"
    magic = MAGIC

    def __init__(
        self,
        profile: str = "max",
        *,
        surface_weight: float = 0.0,
        work_weight: float = 0.0,
        entropy_level: int = 12,
    ) -> None:
        if profile not in {"speed", "balanced", "max"}:
            raise ValueError("profile must be speed, balanced or max")
        if surface_weight < 0 or work_weight < 0:
            raise ValueError("cost weights must be non-negative")
        self.profile = profile
        self.surface_weight = float(surface_weight)
        self.work_weight = float(work_weight)
        self.entropy_level = int(entropy_level)

    def _candidate_key(self, candidate: _RecordCandidate) -> tuple[float, int, int, int]:
        return candidate.cost.key(self.surface_weight, self.work_weight)

    def _encode_block(self, block: bytes) -> _RecordCandidate:
        candidates = [_RecordCandidate(bytes([MODE_RAW]) + block, GabrielCost(1 + len(block), 1, 0))]
        seen_transforms: set[bytes] = set()
        for transform, parameter, work in _transform_specs(len(block), self.profile):
            transformed = _apply_transform(block, transform, parameter)
            digest = hashlib.blake2s(transformed, digest_size=16).digest()
            if digest in seen_transforms:
                continue
            seen_transforms.add(digest)

            prefix = bytes([MODE_ENTROPY, transform]) + _uvarint(parameter)
            for codec, compressed in _entropy_candidates(transformed, self.entropy_level):
                record = prefix + bytes([codec]) + compressed
                candidates.append(_RecordCandidate(record, GabrielCost(len(record), 1, work + 1)))

            shell_payload, active = _encode_shells(transformed, self.entropy_level)
            record = bytes([MODE_SHELLS, transform]) + _uvarint(parameter) + shell_payload
            candidates.append(_RecordCandidate(record, GabrielCost(len(record), active, work + 8)))
        return min(candidates, key=self._candidate_key)

    def _build_archive(self, source: bytes, block_size: int) -> tuple[bytes, GabrielCost]:
        blocks = [source[start:start + block_size] for start in range(0, len(source), block_size)]
        records: list[bytes] = []
        total_shells = total_work = dependency_depth = 0
        seen: dict[tuple[int, bytes], int] = {}

        for index, block in enumerate(blocks):
            best = self._encode_block(block)
            key = (len(block), hashlib.blake2s(block, digest_size=16).digest())
            previous = seen.get(key)
            if previous is not None and blocks[previous] == block:
                reference = bytes([MODE_REFERENCE]) + _uvarint(previous)
                candidate = _RecordCandidate(reference, GabrielCost(len(reference), 0, 0, 1))
                if self._candidate_key(candidate) < self._candidate_key(best):
                    best = candidate
                    dependency_depth += 1
            else:
                seen[key] = index
            records.append(best.record)
            total_shells += best.cost.active_shells
            total_work += best.cost.transform_work

        offsets: list[tuple[int, int]] = []
        cursor = 0
        for record in records:
            offsets.append((cursor, len(record)))
            cursor += len(record)
        index_blob = b"".join(INDEX_ENTRY.pack(offset, length) for offset, length in offsets)
        header = HEADER.pack(MAGIC, VERSION, len(source), block_size, len(blocks), _sha(source))
        archive = header + index_blob + b"".join(records)
        return archive, GabrielCost(len(archive), total_shells, total_work, dependency_depth)

    def compress(self, source: bytes) -> bytes:
        source = bytes(source)
        candidates = [self._build_archive(source, size) for size in _block_sizes(len(source), self.profile)]
        archive, _ = min(candidates, key=lambda item: item[1].key(self.surface_weight, self.work_weight))
        if self.decompress(archive) != source:
            raise ValueError("Gabriel Horn verification failed")
        return archive

    @staticmethod
    def _parse(archive: bytes) -> tuple[int, int, int, bytes, list[tuple[int, int]], int]:
        if len(archive) < HEADER.size:
            raise ValueError("truncated Gabriel archive")
        magic, version, original_size, block_size, block_count, digest = HEADER.unpack_from(archive)
        if magic != MAGIC or version != VERSION:
            raise ValueError("not a supported SHTENCO Gabriel archive")
        if block_size <= 0:
            raise ValueError("invalid Gabriel block size")
        index_end = HEADER.size + block_count * INDEX_ENTRY.size
        if index_end > len(archive):
            raise ValueError("truncated Gabriel block index")
        entries: list[tuple[int, int]] = []
        previous_end = 0
        for i in range(block_count):
            offset, length = INDEX_ENTRY.unpack_from(archive, HEADER.size + i * INDEX_ENTRY.size)
            if offset < previous_end or index_end + offset + length > len(archive):
                raise ValueError("invalid Gabriel block index")
            entries.append((offset, length))
            previous_end = offset + length
        expected_blocks = (original_size + block_size - 1) // block_size if original_size else 0
        if block_count != expected_blocks:
            raise ValueError("Gabriel block count mismatch")
        return original_size, block_size, block_count, digest, entries, index_end

    @staticmethod
    def _decode_record(record: bytes, expected_size: int, decoded: list[bytes], precision_bits: int) -> bytes:
        if not record:
            raise ValueError("empty Gabriel block record")
        mode = record[0]
        if mode == MODE_RAW:
            data = record[1:]
            if len(data) != expected_size:
                raise ValueError("raw Gabriel block size mismatch")
            return data
        if mode == MODE_REFERENCE:
            reference, end = _read_uvarint(record, 1)
            if end != len(record) or reference >= len(decoded):
                raise ValueError("invalid Gabriel block reference")
            data = decoded[reference]
            if len(data) != expected_size:
                raise ValueError("Gabriel reference size mismatch")
            return data
        if mode not in (MODE_ENTROPY, MODE_SHELLS) or len(record) < 3:
            raise ValueError("unknown Gabriel block mode")
        transform = record[1]
        parameter, offset = _read_uvarint(record, 2)
        if mode == MODE_ENTROPY:
            if offset >= len(record):
                raise ValueError("truncated Gabriel entropy record")
            transformed = _entropy_decode(record[offset], record[offset + 1:], expected_size)
        else:
            transformed = _decode_shells(record[offset:], expected_size, precision_bits)
        data = _invert_transform(transformed, transform, parameter)
        if len(data) != expected_size:
            raise ValueError("Gabriel inverse transform size mismatch")
        return data

    def decompress(self, archive: bytes) -> bytes:
        original_size, block_size, _, digest, entries, data_start = self._parse(archive)
        decoded: list[bytes] = []
        for index, (offset, length) in enumerate(entries):
            expected = min(block_size, original_size - index * block_size)
            record = archive[data_start + offset:data_start + offset + length]
            decoded.append(self._decode_record(record, expected, decoded, 8))
        result = b"".join(decoded)
        if len(result) != original_size or _sha(result) != digest:
            raise ValueError("Gabriel size/SHA-256 mismatch")
        return result

    def decompress_progressive(self, archive: bytes, precision_bits: int) -> bytes:
        """Decode the first N significance shells; N=8 is exact."""
        original_size, block_size, _, _, entries, data_start = self._parse(archive)
        decoded: list[bytes] = []
        for index, (offset, length) in enumerate(entries):
            expected = min(block_size, original_size - index * block_size)
            record = archive[data_start + offset:data_start + offset + length]
            decoded.append(self._decode_record(record, expected, decoded, precision_bits))
        return b"".join(decoded)

    def decompress_range(self, archive: bytes, start: int, end: int | None = None) -> bytes:
        """Exact random-access extraction of ``[start:end]``."""
        original_size, block_size, block_count, _, entries, data_start = self._parse(archive)
        if end is None:
            end = original_size
        if start < 0 or end < start or end > original_size:
            raise ValueError("invalid Gabriel range")
        if start == end:
            return b""
        cache: dict[int, bytes] = {}

        def decode_index(index: int) -> bytes:
            if index in cache:
                return cache[index]
            offset, length = entries[index]
            record = archive[data_start + offset:data_start + offset + length]
            expected = min(block_size, original_size - index * block_size)
            if record and record[0] == MODE_REFERENCE:
                reference, marker = _read_uvarint(record, 1)
                if marker != len(record) or reference >= index:
                    raise ValueError("invalid Gabriel random-access reference")
                data = decode_index(reference)
                if len(data) != expected:
                    raise ValueError("Gabriel random-access reference size mismatch")
            else:
                data = self._decode_record(record, expected, [b""] * index, 8)
            cache[index] = data
            return data

        first = start // block_size
        last = (end - 1) // block_size
        if first >= block_count or last >= block_count:
            raise ValueError("Gabriel range outside archive")
        joined = b"".join(decode_index(index) for index in range(first, last + 1))
        left = start - first * block_size
        return joined[left:left + (end - start)]

    def inspect(self, archive: bytes) -> ArchiveInfo:
        original_size, block_size, block_count, _, entries, data_start = self._parse(archive)
        raw = entropy = shells = references = active_shells = 0
        for offset, length in entries:
            record = archive[data_start + offset:data_start + offset + length]
            mode = record[0] if record else -1
            if mode == MODE_RAW:
                raw += 1
            elif mode == MODE_ENTROPY:
                entropy += 1
            elif mode == MODE_SHELLS:
                shells += 1
                _, cursor = _read_uvarint(record, 2)
                if cursor >= len(record) or record[cursor] != 8:
                    raise ValueError("invalid Gabriel shell record")
                cursor += 1
                for _ in range(8):
                    encoding = record[cursor]
                    cursor += 1
                    if encoding != SHELL_ZERO:
                        active_shells += 1
                    if encoding in (SHELL_RAW, SHELL_RLE, SHELL_ZSTD, SHELL_ZLIB):
                        length_, cursor = _read_uvarint(record, cursor)
                        cursor += length_
            elif mode == MODE_REFERENCE:
                references += 1
            else:
                raise ValueError("unknown Gabriel record in archive")
        return ArchiveInfo(
            original_size=original_size,
            block_size=block_size,
            block_count=block_count,
            archive_size=len(archive),
            raw_blocks=raw,
            entropy_blocks=entropy,
            shell_blocks=shells,
            reference_blocks=references,
            active_shells=active_shells,
            ratio=(len(archive) / original_size) if original_size else 0.0,
        )

    @staticmethod
    def shell_tail_bound(precision_bits: int) -> float:
        """Normalized per-coefficient bound after keeping leading bit shells."""
        precision_bits = max(0, min(8, precision_bits))
        if precision_bits == 8:
            return 0.0
        return ((1 << (8 - precision_bits)) - 1) / 255.0


def gabriel_engine_suite() -> list[tuple[str, str, object]]:
    engine = GabrielHornEngine(profile="max")
    return [(engine.name, engine.family, engine)]
