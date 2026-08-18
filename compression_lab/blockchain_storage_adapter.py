#!/usr/bin/env python3
"""Evidence-producing adapter from SHTENCO codecs to SYNERGY archival storage.

The adapter never assumes a compression factor. It measures raw/archive bytes,
verifies exact round-trip equality and emits a content-addressed receipt suitable
for commitment by the SYNERGY storage layer.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Protocol

from .gabriel_horn_engine import GabrielHornEngine


class LosslessCodec(Protocol):
    name: str

    def compress(self, source: bytes) -> bytes: ...
    def decompress(self, archive: bytes) -> bytes: ...


@dataclass(frozen=True, slots=True)
class CodecEvidenceReceipt:
    protocol: str
    codec_name: str
    codec_id: str
    raw_sha256: str
    archive_sha256: str
    raw_bytes: int
    archive_bytes: int
    archive_to_raw_ratio: float
    compression_factor: float
    exact_roundtrip: bool
    chunk_size: int
    chunk_root: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _pair_hash(left: bytes, right: bytes) -> bytes:
    return sha256(b"SYNERGY_ARCHIVE_NODE_V1" + left + right).digest()


def chunk_root(data: bytes, chunk_size: int = 1 << 20) -> str:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    leaves = [
        sha256(b"SYNERGY_ARCHIVE_CHUNK_V1" + i.to_bytes(8, "big") + data[i:i + chunk_size]).digest()
        for i in range(0, len(data), chunk_size)
    ]
    if not leaves:
        leaves = [sha256(b"SYNERGY_ARCHIVE_EMPTY_V1").digest()]
    while len(leaves) > 1:
        if len(leaves) & 1:
            leaves.append(leaves[-1])
        leaves = [_pair_hash(leaves[i], leaves[i + 1]) for i in range(0, len(leaves), 2)]
    return leaves[0].hex()


def codec_id(codec_name: str) -> str:
    return sha256(("SYNERGY_CODEC_V1|" + codec_name).encode()).hexdigest()[:32]


def produce_receipt(source: bytes, codec: LosslessCodec, *, chunk_size: int = 1 << 20) -> tuple[bytes, CodecEvidenceReceipt]:
    source = bytes(source)
    archive = codec.compress(source)
    restored = codec.decompress(archive)
    exact = restored == source and sha256(restored).digest() == sha256(source).digest()
    if not exact:
        raise ValueError("codec failed exact round-trip verification")

    raw_len = len(source)
    archive_len = len(archive)
    ratio = (archive_len / raw_len) if raw_len else 1.0
    factor = (raw_len / archive_len) if archive_len else 0.0
    receipt = CodecEvidenceReceipt(
        protocol="SYNERGY-CODEC-EVIDENCE/1",
        codec_name=codec.name,
        codec_id=codec_id(codec.name),
        raw_sha256=sha256(source).hexdigest(),
        archive_sha256=sha256(archive).hexdigest(),
        raw_bytes=raw_len,
        archive_bytes=archive_len,
        archive_to_raw_ratio=ratio,
        compression_factor=factor,
        exact_roundtrip=True,
        chunk_size=chunk_size,
        chunk_root=chunk_root(archive, chunk_size),
    )
    return archive, receipt


def gabriel_receipt(source: bytes, *, profile: str = "max", chunk_size: int = 1 << 20) -> tuple[bytes, CodecEvidenceReceipt]:
    return produce_receipt(source, GabrielHornEngine(profile=profile), chunk_size=chunk_size)


def choose_smallest_verified(source: bytes, codecs: list[LosslessCodec], *, chunk_size: int = 1 << 20) -> tuple[bytes, CodecEvidenceReceipt]:
    if not codecs:
        raise ValueError("at least one codec required")
    candidates = [produce_receipt(source, codec, chunk_size=chunk_size) for codec in codecs]
    return min(candidates, key=lambda item: (item[1].archive_bytes, item[1].codec_name))
