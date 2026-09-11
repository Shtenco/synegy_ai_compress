#!/usr/bin/env python3
"""NEXUS Ω-Store probe.

Experimental bridge between SHTENCO Tier-1 lossless codecs and a future
random-access LLM weight store.

This is deliberately a *probe*, not a claim that arbitrary quantized weights
compress well. It benchmarks independent fixed-size tiles and keeps RAW as a
first-class winner for incompressible data.

Examples:
    python -m compression_lab.nexus_omega_store_probe --synthetic
    python -m compression_lab.nexus_omega_store_probe --file model.gguf
    python -m compression_lab.nexus_omega_store_probe --file shard.safetensors \
        --block-kib 64 256 1024 --profiles raw omnia-speed omnia-balanced gabriel-ra
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import time
from dataclasses import asdict, dataclass
from typing import Callable, Iterable

try:
    from .shtenco_tier1_v2 import (
        GabrielHornRandomAccessTier1,
        OmniaTier1Balanced,
        OmniaTier1Speed,
    )
except ImportError:  # direct execution from compression_lab/
    from shtenco_tier1_v2 import (
        GabrielHornRandomAccessTier1,
        OmniaTier1Balanced,
        OmniaTier1Speed,
    )


@dataclass(frozen=True)
class TileResult:
    offset: int
    raw_bytes: int
    stored_bytes: int
    profile: str
    route: str
    encode_ms: float
    decode_ms: float
    objective: float


@dataclass(frozen=True)
class ProbeResult:
    name: str
    source_bytes: int
    block_bytes: int
    stored_bytes: int
    ratio: float
    mean_decode_ms: float
    p95_decode_ms: float
    mean_access_amplification: float
    route_counts: dict[str, int]
    sha256: str
    tiles: int


class _Raw:
    name = "raw"
    last_mode = "RAW"

    def compress(self, source: bytes) -> bytes:
        return bytes(source)

    def decompress(self, archive: bytes) -> bytes:
        return bytes(archive)


class _Profile:
    def __init__(self, name: str, factory: Callable[[], object]) -> None:
        self.name = name
        self.factory = factory


PROFILES = {
    "raw": _Profile("raw", _Raw),
    "omnia-speed": _Profile("omnia-speed", OmniaTier1Speed),
    "omnia-balanced": _Profile("omnia-balanced", OmniaTier1Balanced),
    "gabriel-ra": _Profile(
        "gabriel-ra",
        lambda: GabrielHornRandomAccessTier1(expected_range_bytes=4096, access_weight=96.0),
    ),
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _quantile95(values: list[float]) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    return values[min(len(values) - 1, math.ceil(0.95 * len(values)) - 1)]


def _candidate(
    block: bytes,
    profile: _Profile,
    *,
    expected_read_bytes: int,
    decode_ms_penalty: float,
    access_penalty: float,
) -> tuple[float, TileResult, bytes]:
    engine = profile.factory()

    started = time.perf_counter()
    archive = engine.compress(block)
    encode_ms = (time.perf_counter() - started) * 1000.0

    started = time.perf_counter()
    restored = engine.decompress(archive)
    decode_ms = (time.perf_counter() - started) * 1000.0

    if restored != block or hashlib.sha256(restored).digest() != hashlib.sha256(block).digest():
        raise ValueError(f"{profile.name} failed exact round-trip verification")

    # A tile is the minimum fetch unit in this probe. Penalize both decode
    # latency and the extra bytes fetched for a small logical request.
    logical = max(1, min(len(block), expected_read_bytes))
    amplification = len(archive) / logical
    objective = len(archive) + decode_ms_penalty * decode_ms + access_penalty * amplification
    route = str(getattr(engine, "last_mode", profile.name))
    row = TileResult(
        offset=0,
        raw_bytes=len(block),
        stored_bytes=len(archive),
        profile=profile.name,
        route=route,
        encode_ms=encode_ms,
        decode_ms=decode_ms,
        objective=objective,
    )
    return objective, row, archive


def probe_bytes(
    name: str,
    source: bytes,
    *,
    block_bytes: int,
    profiles: Iterable[str],
    expected_read_bytes: int = 4096,
    decode_ms_penalty: float = 256.0,
    access_penalty: float = 4096.0,
) -> ProbeResult:
    if block_bytes <= 0:
        raise ValueError("block_bytes must be > 0")
    chosen_profiles = [PROFILES[p] for p in profiles]
    if not chosen_profiles:
        raise ValueError("at least one profile is required")

    rows: list[TileResult] = []
    reconstructed = bytearray()
    stored_total = 0
    route_counts: dict[str, int] = {}

    for offset in range(0, len(source), block_bytes):
        block = source[offset : offset + block_bytes]
        candidates = [
            _candidate(
                block,
                profile,
                expected_read_bytes=expected_read_bytes,
                decode_ms_penalty=decode_ms_penalty,
                access_penalty=access_penalty,
            )
            for profile in chosen_profiles
        ]
        _, best, _ = min(
            candidates,
            key=lambda item: (
                item[0],
                item[1].stored_bytes,
                item[1].decode_ms,
                item[1].profile,
            ),
        )

        # Recreate with the winning profile so the stored representation is
        # independently verified in the same way a future index reader would.
        winner = PROFILES[best.profile].factory()
        archive = winner.compress(block)
        restored = winner.decompress(archive)
        if restored != block:
            raise ValueError(f"winner {best.profile} failed final verification")

        rows.append(
            TileResult(
                offset=offset,
                raw_bytes=best.raw_bytes,
                stored_bytes=len(archive),
                profile=best.profile,
                route=str(getattr(winner, "last_mode", best.route)),
                encode_ms=best.encode_ms,
                decode_ms=best.decode_ms,
                objective=best.objective,
            )
        )
        reconstructed.extend(restored)
        stored_total += len(archive)
        key = f"{best.profile}:{rows[-1].route}"
        route_counts[key] = route_counts.get(key, 0) + 1

    if bytes(reconstructed) != source or _sha(bytes(reconstructed)) != _sha(source):
        raise ValueError("whole-source reconstruction failed")

    decode_times = [row.decode_ms for row in rows]
    amplifications = [
        row.stored_bytes / max(1, min(row.raw_bytes, expected_read_bytes)) for row in rows
    ]
    return ProbeResult(
        name=name,
        source_bytes=len(source),
        block_bytes=block_bytes,
        stored_bytes=stored_total,
        ratio=(len(source) / stored_total) if stored_total else 1.0,
        mean_decode_ms=statistics.fmean(decode_times) if decode_times else 0.0,
        p95_decode_ms=_quantile95(decode_times),
        mean_access_amplification=statistics.fmean(amplifications) if amplifications else 1.0,
        route_counts=route_counts,
        sha256=_sha(source),
        tiles=len(rows),
    )


def _pack_sparse_bits(rng: random.Random, nbytes: int, one_probability: float) -> bytes:
    out = bytearray(nbytes)
    for i in range(nbytes):
        value = 0
        for bit in range(8):
            if rng.random() < one_probability:
                value |= 1 << bit
        out[i] = value
    return bytes(out)


def _pack_ternary_2bit(rng: random.Random, nbytes: int, zero_probability: float) -> bytes:
    # code 0 -> zero, 1/2 -> signed non-zero states; code 3 remains unused.
    out = bytearray(nbytes)
    side = (1.0 - zero_probability) / 2.0
    for i in range(nbytes):
        value = 0
        for slot in range(4):
            u = rng.random()
            code = 0 if u < zero_probability else (1 if u < zero_probability + side else 2)
            value |= code << (2 * slot)
        out[i] = value
    return bytes(out)


def _correlated_binary_rows(
    rng: random.Random,
    nbytes: int,
    *,
    row_bytes: int = 1024,
    bit_flip_probability: float = 0.01,
) -> bytes:
    base = bytearray(rng.getrandbits(8) for _ in range(row_bytes))
    out = bytearray()
    while len(out) < nbytes:
        row = bytearray(base)
        for i, value in enumerate(row):
            mask = 0
            for bit in range(8):
                if rng.random() < bit_flip_probability:
                    mask |= 1 << bit
            row[i] = value ^ mask
        out.extend(row)
    return bytes(out[:nbytes])


def synthetic_corpus(size: int = 512 * 1024, seed: int = 20260911) -> dict[str, bytes]:
    rng = random.Random(seed)
    return {
        "binary-50-50-packed": bytes(rng.getrandbits(8) for _ in range(size)),
        "binary-10pct-ones": _pack_sparse_bits(rng, size, 0.10),
        "activation-mask-3pct": _pack_sparse_bits(rng, size, 0.03),
        "ternary-60pct-zero-2bit": _pack_ternary_2bit(rng, size, 0.60),
        "binary-factor-correlated-rows": _correlated_binary_rows(rng, size),
    }


def _emit(results: list[ProbeResult], output: Path | None) -> None:
    payload = {
        "schema": "shtenco.nexus-omega-store-probe/v1",
        "results": [asdict(row) for row in results],
    }
    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if output is not None:
        output.write_text(text + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", type=Path)
    group.add_argument("--synthetic", action="store_true")
    parser.add_argument("--block-kib", nargs="+", type=int, default=[64, 256, 1024])
    parser.add_argument(
        "--profiles",
        nargs="+",
        choices=sorted(PROFILES),
        default=["raw", "omnia-speed", "omnia-balanced", "gabriel-ra"],
    )
    parser.add_argument("--expected-read-kib", type=int, default=4)
    parser.add_argument("--decode-ms-penalty", type=float, default=256.0)
    parser.add_argument("--access-penalty", type=float, default=4096.0)
    parser.add_argument("--synthetic-kib", type=int, default=512)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.synthetic:
        sources = synthetic_corpus(args.synthetic_kib * 1024)
    else:
        path = args.file
        if path is None or not path.is_file():
            parser.error("--file must point to a regular file")
        sources = {str(path): path.read_bytes()}

    results: list[ProbeResult] = []
    for name, data in sources.items():
        for kib in args.block_kib:
            results.append(
                probe_bytes(
                    name,
                    data,
                    block_bytes=kib * 1024,
                    profiles=args.profiles,
                    expected_read_bytes=args.expected_read_kib * 1024,
                    decode_ms_penalty=args.decode_ms_penalty,
                    access_penalty=args.access_penalty,
                )
            )

    _emit(results, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
