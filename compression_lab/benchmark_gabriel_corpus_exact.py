#!/usr/bin/env python3
"""Exact benchmark front-end that records variable archive sizes honestly.

Some historical engines embed run-dependent metadata or select equal-cost expert
paths non-deterministically. This front-end keeps byte/SHA correctness strict,
uses the median archive size for ranking, and writes min/max/span for every row.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
import statistics

try:
    from . import benchmark_gabriel_corpus as base
except ImportError:
    import benchmark_gabriel_corpus as base

_VARIABILITY: list[dict[str, object]] = []


def _median_row(dataset: base.Dataset, results: list[base.WorkerResult]) -> base.BenchmarkRow:
    first = results[0]
    if any(r.sha256 != first.sha256 or r.input_bytes != first.input_bytes for r in results):
        raise RuntimeError(f"source identity changed across repetitions for {first.engine}")
    sizes = [r.archive_bytes for r in results]
    median_size = int(statistics.median(sizes))
    _VARIABILITY.append({
        "dataset": dataset.name,
        "engine_id": first.engine_id,
        "engine": first.engine,
        "repetitions": len(results),
        "archive_bytes_median": median_size,
        "archive_bytes_min": min(sizes),
        "archive_bytes_max": max(sizes),
        "archive_size_span": max(sizes) - min(sizes),
        "observed_sizes": sizes,
    })
    input_mib = first.input_bytes / base.MiB
    encode_ms = statistics.median(r.encode_ns for r in results) / 1e6
    decode_ms = statistics.median(r.decode_ns for r in results) / 1e6
    random_ns = statistics.median(r.random_access_ns for r in results)
    requested = statistics.median(r.requested_bytes for r in results)
    inflated = statistics.median(r.logical_bytes_inflated for r in results)
    ratio = median_size / first.input_bytes if first.input_bytes else 0.0
    return base.BenchmarkRow(
        dataset=dataset.name,
        dataset_kind=dataset.kind,
        source=dataset.source,
        engine_id=first.engine_id,
        engine=first.engine,
        family=first.family,
        native_random_access=first.native_random_access,
        input_bytes=first.input_bytes,
        archive_bytes=median_size,
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


def _write_variability(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "archive_size_variability.json").write_text(
        json.dumps(_VARIABILITY, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if _VARIABILITY:
        rows = []
        for item in _VARIABILITY:
            row = dict(item)
            row["observed_sizes"] = ";".join(str(value) for value in item["observed_sizes"])
            rows.append(row)
        with (output / "archive_size_variability.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)

        markdown = output / "GABRIEL_CORPUS_BENCHMARK.md"
        with markdown.open("a", encoding="utf-8") as handle:
            handle.write("\n## Archive-size variability\n\n")
            handle.write("Ranking uses the median archive size. A non-zero span is retained, not hidden.\n\n")
            handle.write("| Dataset | Engine | Median | Min | Max | Span | Observed |\n")
            handle.write("|---|---|---:|---:|---:|---:|---|\n")
            for item in _VARIABILITY:
                handle.write(
                    f"| {item['dataset']} | {item['engine']} | {item['archive_bytes_median']} | "
                    f"{item['archive_bytes_min']} | {item['archive_bytes_max']} | "
                    f"{item['archive_size_span']} | {item['observed_sizes']} |\n"
                )

    report_path = output / "gabriel_corpus_report.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report.setdefault("metadata", {})["archive_size_variability"] = _VARIABILITY
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    args = base.parser().parse_args()
    if args.worker:
        if not args.input:
            raise SystemExit("--worker requires --input")
        return base._worker_cli(args)
    if args.size < 0 or args.repeats < 1 or args.warmups < 0:
        raise SystemExit("invalid benchmark dimensions")
    base._median_row = _median_row
    code = base.run_benchmark(args)
    _write_variability(Path(args.output))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
