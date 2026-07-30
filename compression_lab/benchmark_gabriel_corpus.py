#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exact, reproducible corpus benchmark for SHTENCO Gabriel Horn.

The benchmark compares actual archive bytes, encode/decode throughput, process
peak RSS and random-range extraction cost. Every measured repetition is run in a
fresh worker process and must pass byte equality plus SHA-256 verification.

Historical UMC-256 is loaded only when its exact snapshot module is importable;
it is never silently replaced by another engine. Use --require-umc in the exact
private-snapshot workflow.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import hashlib
import importlib
import json
import math
from pathlib import Path
import platform
import random
import statistics
import struct
import subprocess
import sys
import tempfile
import time
from typing import Callable, Iterable, Protocol

MiB = 1024 * 1024
ENGINE_ORDER = ("raw", "gabriel-max", "zstd-19", "brotli-11", "umc256-max", "graal-igc")


class Codec(Protocol):
    def compress(self, source: bytes) -> bytes: ...
    def decompress(self, archive: bytes) -> bytes: ...


@dataclass(frozen=True)
class Dataset:
    name: str
    data: bytes
    kind: str
    source: str


@dataclass(frozen=True)
class WorkerResult:
    engine_id: str
    engine: str
    family: str
    native_random_access: bool
    input_bytes: int
    archive_bytes: int
    encode_ns: int
    decode_ns: int
    random_access_ns: int
    random_queries: int
    requested_bytes: int
    logical_bytes_inflated: int
    peak_rss_mib: float
    sha256: str
    status: str


@dataclass(frozen=True)
class BenchmarkRow:
    dataset: str
    dataset_kind: str
    source: str
    engine_id: str
    engine: str
    family: str
    native_random_access: bool
    input_bytes: int
    archive_bytes: int
    ratio: float
    savings_pct: float
    bits_per_byte: float
    encode_ms: float
    decode_ms: float
    encode_mib_s: float
    decode_mib_s: float
    peak_rss_mib: float
    random_access_us: float
    access_amplification: float
    repetitions: int
    sha256: str
    status: str


class _RawCodec:
    def compress(self, source: bytes) -> bytes:
        return bytes(source)

    def decompress(self, archive: bytes) -> bytes:
        return bytes(archive)


class _ZstdCodec:
    def __init__(self, level: int = 19) -> None:
        import zstandard as zstd
        self._compressor = zstd.ZstdCompressor(
            level=level, write_checksum=True, write_content_size=True, write_dict_id=False
        )
        self._decompressor = zstd.ZstdDecompressor()

    def compress(self, source: bytes) -> bytes:
        return self._compressor.compress(source)

    def decompress(self, archive: bytes) -> bytes:
        return self._decompressor.decompress(archive)


class _BrotliCodec:
    def __init__(self, quality: int = 11) -> None:
        import brotli
        self._brotli = brotli
        self._quality = quality

    def compress(self, source: bytes) -> bytes:
        return self._brotli.compress(source, quality=self._quality, mode=self._brotli.MODE_GENERIC)

    def decompress(self, archive: bytes) -> bytes:
        return self._brotli.decompress(archive)


@dataclass(frozen=True)
class EngineSpec:
    engine_id: str
    name: str
    family: str
    native_random_access: bool
    factory: Callable[[], Codec]


def _import_attr(candidates: Iterable[tuple[str, str]]) -> object:
    errors: list[str] = []
    for module_name, attr_name in candidates:
        try:
            module = importlib.import_module(module_name)
            return getattr(module, attr_name)
        except Exception as exc:
            errors.append(f"{module_name}.{attr_name}: {type(exc).__name__}: {exc}")
    raise ImportError("; ".join(errors))


def engine_specs() -> dict[str, EngineSpec]:
    specs: dict[str, EngineSpec] = {
        "raw": EngineSpec("raw", "RAW baseline", "BASELINE", False, _RawCodec),
    }
    try:
        import zstandard  # noqa: F401
        specs["zstd-19"] = EngineSpec(
            "zstd-19", "Zstandard level 19", "STANDARD", False, _ZstdCodec
        )
    except Exception:
        pass
    try:
        import brotli  # noqa: F401
        specs["brotli-11"] = EngineSpec(
            "brotli-11", "Brotli quality 11", "STANDARD", False, _BrotliCodec
        )
    except Exception:
        pass

    try:
        Gabriel = _import_attr((("compression_lab.gabriel_horn_engine", "GabrielHornEngine"),
                                ("gabriel_horn_engine", "GabrielHornEngine")))
        specs["gabriel-max"] = EngineSpec(
            "gabriel-max", "SHTENCO Gabriel Horn MAX", "SHTENCO-GABRIEL", True,
            lambda: Gabriel(profile="max", surface_weight=0.0, work_weight=0.0),
        )
    except ImportError:
        pass

    try:
        Graal = _import_attr((("compression_lab.shtenco_tier1_engines", "GRAALIGCTier1Max"),
                             ("shtenco_tier1_engines", "GRAALIGCTier1Max")))
        specs["graal-igc"] = EngineSpec(
            "graal-igc", "SHTENCO GRAAL-IGC TIER1 MAX", "SHTENCO-TIER1", False, Graal,
        )
    except ImportError:
        pass

    try:
        UMC = _import_attr((("compression_lab.umc256_engine", "UMC256Engine"),
                           ("umc256_engine", "UMC256Engine")))
        specs["umc256-max"] = EngineSpec(
            "umc256-max", "SHTENCO UMC-256 MAX (latency weight 0)", "SHTENCO-UMC256", False,
            lambda: UMC(mode="max", latency_weight=0.0),
        )
    except ImportError:
        pass
    return specs


def _fit(data: bytes, size: int) -> bytes:
    if size <= 0:
        return b""
    if not data:
        return bytes(size)
    repeats = (size + len(data) - 1) // len(data)
    return (data * repeats)[:size]


def _english_text(size: int) -> bytes:
    paragraphs = []
    for i in range(256):
        paragraphs.append(
            f"Record {i:04d}: finite stored volume and bounded access surface. "
            f"A reversible model keeps exact symbols while residual shells narrow toward zero. "
            f"The block checksum is {hashlib.sha256(str(i).encode()).hexdigest()[:16]}.\n"
        )
    return _fit("".join(paragraphs).encode("utf-8"), size)


def _json_records(size: int) -> bytes:
    rows = []
    for i in range(512):
        rows.append({
            "id": i,
            "symbol": ("EURUSD", "GBPUSD", "USDJPY", "XAUUSD")[i % 4],
            "side": "buy" if i % 2 == 0 else "sell",
            "price": round(1.05 + (i % 97) * 0.0001, 5),
            "volume": (i % 13) + 1,
            "active": i % 7 != 0,
        })
    blob = "\n".join(json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows).encode()
    return _fit(blob, size)


def _numeric_smooth(size: int) -> bytes:
    out = bytearray()
    count = max(1, (size + 3) // 4)
    for i in range(count):
        value = int(1_000_000 + 130_000 * math.sin(i / 91.0) + i * 3)
        out += struct.pack("<i", value)
    return bytes(out[:size])


def _versioned_blocks(size: int) -> bytes:
    rng = random.Random(0xBADC0DE)
    block_size = 1024
    base = bytearray((i * 17 + i // 7) & 255 for i in range(block_size))
    out = bytearray()
    version = bytearray(base)
    while len(out) < size:
        if (len(out) // block_size) % 4 == 0:
            version = bytearray(base)
        else:
            for _ in range(6):
                pos = rng.randrange(block_size)
                version[pos] ^= rng.randrange(1, 256)
        out += version
    return bytes(out[:size])


def _sparse_binary(size: int) -> bytes:
    out = bytearray(size)
    for i in range(0, size, 257):
        marker = hashlib.blake2s(struct.pack(">I", i), digest_size=12).digest()
        out[i:min(size, i + len(marker))] = marker[:max(0, size - i)]
    return bytes(out)


def _source_code(size: int) -> bytes:
    chunks = []
    for i in range(400):
        chunks.append(
            f"def transform_{i}(data: bytes, lag: int = {(i % 32) + 1}) -> bytes:\n"
            f"    out = bytearray(len(data))\n"
            f"    for p, value in enumerate(data):\n"
            f"        out[p] = value ^ (data[p-lag] if p >= lag else 0)\n"
            f"    return bytes(out)\n\n"
        )
    return _fit("".join(chunks).encode(), size)


def _random_bytes(size: int) -> bytes:
    rng = random.Random(0x53474831)
    return bytes(rng.randrange(256) for _ in range(size))


def built_in_corpus(size: int) -> list[Dataset]:
    makers = (
        ("english_text", "text", _english_text),
        ("json_records", "structured", _json_records),
        ("numeric_smooth_i32", "numeric", _numeric_smooth),
        ("versioned_blocks", "versioned", _versioned_blocks),
        ("sparse_binary", "sparse", _sparse_binary),
        ("source_code", "code", _source_code),
        ("seeded_random", "high_entropy", _random_bytes),
    )
    return [Dataset(name, maker(size), kind, "builtin-v1") for name, kind, maker in makers]


def directory_corpus(path: Path, max_bytes: int) -> list[Dataset]:
    datasets = []
    for file in sorted(p for p in path.rglob("*") if p.is_file()):
        data = file.read_bytes()[:max_bytes]
        if data:
            datasets.append(Dataset(file.relative_to(path).as_posix(), data, "external", str(file)))
    return datasets


def _peak_rss_mib() -> float:
    try:
        import resource
        value = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        return value / MiB if sys.platform == "darwin" else value / 1024.0
    except Exception:
        try:
            import psutil
            return psutil.Process().memory_info().rss / MiB
        except Exception:
            return float("nan")


def _query_ranges(size: int, count: int, requested: int) -> list[tuple[int, int]]:
    if size == 0:
        return [(0, 0)]
    width = max(1, min(size, requested))
    rng = random.Random(size ^ 0x4741425249454C)
    ranges = []
    for _ in range(max(1, count)):
        start = rng.randrange(0, size - width + 1)
        ranges.append((start, start + width))
    return ranges


def _run_worker(engine_id: str, input_path: Path, random_queries: int,
                random_bytes: int) -> WorkerResult:
    source = input_path.read_bytes()
    specs = engine_specs()
    if engine_id not in specs:
        raise RuntimeError(f"engine {engine_id!r} is unavailable in worker")
    spec = specs[engine_id]
    codec = spec.factory()

    started = time.perf_counter_ns()
    archive = codec.compress(source)
    encode_ns = time.perf_counter_ns() - started

    started = time.perf_counter_ns()
    restored = codec.decompress(archive)
    decode_ns = time.perf_counter_ns() - started
    digest = hashlib.sha256(source).hexdigest()
    if restored != source or hashlib.sha256(restored).hexdigest() != digest:
        raise RuntimeError(f"{spec.name} failed exact round-trip")

    timings = []
    requested_total = logical_total = 0
    for start, end in _query_ranges(len(source), random_queries, random_bytes):
        tick = time.perf_counter_ns()
        if spec.native_random_access:
            fragment = codec.decompress_range(archive, start, end)  # type: ignore[attr-defined]
            info = codec.inspect(archive)  # type: ignore[attr-defined]
            first = start // info.block_size if end > start else 0
            last = (end - 1) // info.block_size if end > start else first
            logical = min(len(source), (last + 1) * info.block_size) - first * info.block_size
        else:
            fragment = codec.decompress(archive)[start:end]
            logical = len(source)
        timings.append(time.perf_counter_ns() - tick)
        if fragment != source[start:end]:
            raise RuntimeError(f"{spec.name} failed random-range verification")
        requested_total += end - start
        logical_total += logical

    return WorkerResult(
        engine_id=engine_id,
        engine=spec.name,
        family=spec.family,
        native_random_access=spec.native_random_access,
        input_bytes=len(source),
        archive_bytes=len(archive),
        encode_ns=encode_ns,
        decode_ns=decode_ns,
        random_access_ns=int(statistics.median(timings)) if timings else 0,
        random_queries=len(timings),
        requested_bytes=requested_total,
        logical_bytes_inflated=logical_total,
        peak_rss_mib=_peak_rss_mib(),
        sha256=digest,
        status="PASS",
    )


def _worker_cli(args: argparse.Namespace) -> int:
    result = _run_worker(args.worker, Path(args.input), args.random_queries, args.random_bytes)
    print(json.dumps(asdict(result), sort_keys=True))
    return 0


def _invoke_worker(script: Path, engine_id: str, input_path: Path,
                   random_queries: int, random_bytes: int) -> WorkerResult:
    command = [sys.executable, str(script), "--worker", engine_id, "--input", str(input_path),
               "--random-queries", str(random_queries), "--random-bytes", str(random_bytes)]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            f"worker failed for {engine_id}: returncode={completed.returncode}\n"
            f"stdout={completed.stdout}\nstderr={completed.stderr}"
        )
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError(f"worker {engine_id} returned no JSON")
    return WorkerResult(**json.loads(lines[-1]))


def _median_row(dataset: Dataset, results: list[WorkerResult]) -> BenchmarkRow:
    first = results[0]
    if any(r.archive_bytes != first.archive_bytes or r.sha256 != first.sha256 for r in results):
        raise RuntimeError(f"non-deterministic archive size or source hash for {first.engine}")
    input_mib = first.input_bytes / MiB
    encode_ms = statistics.median(r.encode_ns for r in results) / 1e6
    decode_ms = statistics.median(r.decode_ns for r in results) / 1e6
    ratio = first.archive_bytes / first.input_bytes if first.input_bytes else 0.0
    random_ns = statistics.median(r.random_access_ns for r in results)
    requested = statistics.median(r.requested_bytes for r in results)
    inflated = statistics.median(r.logical_bytes_inflated for r in results)
    return BenchmarkRow(
        dataset=dataset.name,
        dataset_kind=dataset.kind,
        source=dataset.source,
        engine_id=first.engine_id,
        engine=first.engine,
        family=first.family,
        native_random_access=first.native_random_access,
        input_bytes=first.input_bytes,
        archive_bytes=first.archive_bytes,
        ratio=ratio,
        savings_pct=(1.0 - ratio) * 100.0,
        bits_per_byte=ratio * 8.0,
        encode_ms=encode_ms,
        decode_ms=decode_ms,
        encode_mib_s=(input_mib / (encode_ms / 1000.0)) if encode_ms > 0 else float("inf"),
        decode_mib_s=(input_mib / (decode_ms / 1000.0)) if decode_ms > 0 else float("inf"),
        peak_rss_mib=statistics.median(r.peak_rss_mib for r in results),
        random_access_us=random_ns / 1000.0,
        access_amplification=(inflated / requested) if requested else 0.0,
        repetitions=len(results),
        sha256=first.sha256,
        status="PASS",
    )


def _summary(rows: list[BenchmarkRow]) -> list[dict[str, object]]:
    output = []
    for engine_id in ENGINE_ORDER:
        subset = [r for r in rows if r.engine_id == engine_id and r.status == "PASS"]
        if not subset:
            continue
        total_in = sum(r.input_bytes for r in subset)
        total_out = sum(r.archive_bytes for r in subset)
        output.append({
            "engine_id": engine_id,
            "engine": subset[0].engine,
            "datasets": len(subset),
            "total_input_bytes": total_in,
            "total_archive_bytes": total_out,
            "ratio": total_out / total_in if total_in else 0.0,
            "savings_pct": (1.0 - total_out / total_in) * 100.0 if total_in else 0.0,
            "median_encode_mib_s": statistics.median(r.encode_mib_s for r in subset),
            "median_decode_mib_s": statistics.median(r.decode_mib_s for r in subset),
            "median_peak_rss_mib": statistics.median(r.peak_rss_mib for r in subset),
            "median_random_access_us": statistics.median(r.random_access_us for r in subset),
            "median_access_amplification": statistics.median(r.access_amplification for r in subset),
            "native_random_access": subset[0].native_random_access,
            "status": "PASS",
        })
    return sorted(output, key=lambda item: (item["total_archive_bytes"], item["engine_id"]))


def _fmt(value: object, digits: int = 3) -> str:
    return f"{float(value):.{digits}f}"


def _write_reports(output: Path, rows: list[BenchmarkRow], summary: list[dict[str, object]],
                   metadata: dict[str, object]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    row_dicts = [asdict(row) for row in rows]
    report = {"metadata": metadata, "summary": summary, "rows": row_dicts}
    (output / "gabriel_corpus_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    if row_dicts:
        with (output / "gabriel_corpus_rows.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(row_dicts[0]))
            writer.writeheader(); writer.writerows(row_dicts)
    if summary:
        with (output / "gabriel_corpus_summary.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
            writer.writeheader(); writer.writerows(summary)

    lines = [
        "# SHTENCO Gabriel Horn exact corpus benchmark", "",
        "Every measured repetition ran in a fresh process and passed byte equality plus SHA-256.",
        "Historical UMC-256 is included only when its exact snapshot module was loaded.", "",
        "## Aggregate ranking", "",
        "| Rank | Engine | Archive bytes | Ratio | Savings | Encode MiB/s | Decode MiB/s | Peak RSS MiB | Range µs | Amplification | Native range |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for rank, item in enumerate(summary, 1):
        lines.append(
            f"| {rank} | {item['engine']} | {item['total_archive_bytes']} | "
            f"{_fmt(item['ratio'], 4)} | {_fmt(item['savings_pct'], 2)}% | "
            f"{_fmt(item['median_encode_mib_s'], 2)} | {_fmt(item['median_decode_mib_s'], 2)} | "
            f"{_fmt(item['median_peak_rss_mib'], 2)} | {_fmt(item['median_random_access_us'], 2)} | "
            f"{_fmt(item['median_access_amplification'], 2)}x | "
            f"{'yes' if item['native_random_access'] else 'no'} |"
        )
    lines += ["", "## Per-dataset archive bytes", "",
              "| Dataset | Input | " + " | ".join(str(item["engine_id"]) for item in summary) + " |",
              "|---|---:|" + "---:|" * len(summary)]
    for dataset in sorted({row.dataset for row in rows}):
        by_engine = {row.engine_id: row.archive_bytes for row in rows if row.dataset == dataset}
        input_size = next(row.input_bytes for row in rows if row.dataset == dataset)
        lines.append(f"| {dataset} | {input_size} | " + " | ".join(str(by_engine.get(str(item["engine_id"]), "—")) for item in summary) + " |")
    lines += ["", "## Configuration", "", "```json", json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True), "```", ""]
    (output / "GABRIEL_CORPUS_BENCHMARK.md").write_text("\n".join(lines), encoding="utf-8")


def run_benchmark(args: argparse.Namespace) -> int:
    specs = engine_specs()
    selected = [value.strip() for value in args.engines.split(",") if value.strip()]
    missing = [engine for engine in selected if engine not in specs]
    if args.require_umc and "umc256-max" not in specs:
        missing.append("umc256-max (exact historical module required)")
    if missing:
        raise SystemExit("Unavailable engines: " + ", ".join(dict.fromkeys(missing)))

    corpus = built_in_corpus(args.size)
    if args.corpus_dir:
        corpus += directory_corpus(Path(args.corpus_dir), args.max_file_bytes)
    if args.datasets:
        wanted = {item.strip() for item in args.datasets.split(",") if item.strip()}
        corpus = [item for item in corpus if item.name in wanted]
    if not corpus:
        raise SystemExit("Corpus is empty")

    output = Path(args.output)
    script = Path(__file__).resolve()
    rows: list[BenchmarkRow] = []
    failures: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="shtenco-gabriel-bench-") as temp:
        temp_path = Path(temp)
        for dataset in corpus:
            input_path = temp_path / (hashlib.sha256(dataset.name.encode()).hexdigest() + ".bin")
            input_path.write_bytes(dataset.data)
            for engine_id in selected:
                print(f"[benchmark] dataset={dataset.name} engine={engine_id}", flush=True)
                try:
                    for _ in range(args.warmups):
                        _invoke_worker(script, engine_id, input_path, args.random_queries, args.random_bytes)
                    results = [
                        _invoke_worker(script, engine_id, input_path, args.random_queries, args.random_bytes)
                        for _ in range(args.repeats)
                    ]
                    rows.append(_median_row(dataset, results))
                except Exception as exc:
                    failures.append({"dataset": dataset.name, "engine_id": engine_id,
                                     "error": f"{type(exc).__name__}: {exc}"})
                    print(f"[failure] {dataset.name}/{engine_id}: {exc}", file=sys.stderr, flush=True)
                    if args.fail_fast:
                        raise

    summary = _summary(rows)
    metadata = {
        "schema": 1,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "size_per_builtin_dataset": args.size,
        "repeats": args.repeats,
        "warmups": args.warmups,
        "random_queries": args.random_queries,
        "random_bytes": args.random_bytes,
        "selected_engines": selected,
        "available_engines": sorted(specs),
        "corpus": [{"name": d.name, "kind": d.kind, "bytes": len(d.data),
                    "sha256": hashlib.sha256(d.data).hexdigest(), "source": d.source} for d in corpus],
        "failures": failures,
        "notes": {
            "ratio": "archive_bytes / input_bytes; lower is better",
            "peak_rss": "absolute fresh-worker process peak RSS, including interpreter and native libraries",
            "random_access": "native range decode where available; otherwise full decode then slice",
            "umc256": "exact snapshot implementation only; latency_weight=0 for size-oriented MAX comparison",
        },
    }
    _write_reports(output, rows, summary, metadata)
    print(json.dumps({"summary": summary, "failures": failures}, ensure_ascii=False, indent=2))
    return 1 if failures else 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", default="compression_lab/output_gabriel_corpus")
    p.add_argument("--size", type=int, default=16384)
    p.add_argument("--repeats", type=int, default=3)
    p.add_argument("--warmups", type=int, default=1)
    p.add_argument("--random-queries", type=int, default=7)
    p.add_argument("--random-bytes", type=int, default=1024)
    p.add_argument("--engines", default=",".join(ENGINE_ORDER))
    p.add_argument("--datasets", default="")
    p.add_argument("--corpus-dir")
    p.add_argument("--max-file-bytes", type=int, default=1 * MiB)
    p.add_argument("--require-umc", action="store_true")
    p.add_argument("--fail-fast", action="store_true")
    p.add_argument("--worker", help=argparse.SUPPRESS)
    p.add_argument("--input", help=argparse.SUPPRESS)
    return p


def main() -> int:
    args = parser().parse_args()
    if args.worker:
        if not args.input:
            raise SystemExit("--worker requires --input")
        return _worker_cli(args)
    if args.size < 0 or args.repeats < 1 or args.warmups < 0:
        raise SystemExit("invalid benchmark dimensions")
    return run_benchmark(args)


if __name__ == "__main__":
    raise SystemExit(main())
