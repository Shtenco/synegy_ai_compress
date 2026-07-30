#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unified exact benchmark: every historical system plus current Tier-1 v1/v2.

The historical benchmark implementation is loaded from the immutable compression
snapshot specified by ``SHTENCO_LEGACY_COMPRESSION_DIR``. Current engines are
loaded from this repository first, then appended without duplicate names.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# Import current production suites before the legacy path can shadow their names.
from shtenco_tier1_engines import tier1_engine_suite
from shtenco_tier1_v2 import tier1_v2_engine_suite

LEGACY = Path(os.environ.get("SHTENCO_LEGACY_COMPRESSION_DIR", "")).resolve()
if not LEGACY.is_dir():
    raise SystemExit(
        "SHTENCO_LEGACY_COMPRESSION_DIR must point to the immutable snapshot's compression_lab directory"
    )
sys.path.insert(0, str(LEGACY))

import benchmark_all_systems_exact as benchmark  # type: ignore  # noqa: E402

_ORIGINAL_BUILD_SYSTEMS = benchmark.build_systems


def build_unified_systems() -> list[Any]:
    systems = _ORIGINAL_BUILD_SYSTEMS()
    seen = {item.name for item in systems}
    for suite in (tier1_engine_suite(), tier1_v2_engine_suite()):
        for name, family, engine in suite:
            if name in seen:
                continue
            systems.append(benchmark.SystemSpec(name, family, engine))
            seen.add(name)
    return systems


def _output_path(argv: list[str]) -> Path:
    for index, value in enumerate(argv):
        if value == "--output" and index + 1 < len(argv):
            return Path(argv[index + 1])
        if value.startswith("--output="):
            return Path(value.split("=", 1)[1])
    return LEGACY / "output_unified_tier1"


def _rank_map(items: list[dict[str, Any]], key: str, reverse: bool) -> dict[str, int]:
    eligible = [item for item in items if item.get("full_pass")]
    ordered = sorted(eligible, key=lambda item: float(item.get(key) or 0.0), reverse=reverse)
    return {item["engine"]: index + 1 for index, item in enumerate(ordered)}


def _write_unified_findings(output: Path) -> None:
    report_path = output / "all_systems_report.json"
    if not report_path.exists():
        return
    report = json.loads(report_path.read_text(encoding="utf-8"))
    summary = report.get("summary", [])
    rows = report.get("rows", [])
    ratio_ranks = _rank_map(summary, "geomean_ratio", True)
    score_ranks = _rank_map(summary, "geomean_score", True)
    balanced_ranks = _rank_map(summary, "geomean_balanced_score", True)
    speed_ranks = _rank_map(summary, "total_encode_ms", False)

    proprietary = []
    for item in summary:
        if not str(item.get("engine", "")).startswith("SHTENCO"):
            continue
        enriched = dict(item)
        name = enriched["engine"]
        enriched.update(
            ratio_rank=ratio_ranks.get(name),
            score_rank=score_ranks.get(name),
            balanced_rank=balanced_ranks.get(name),
            speed_rank=speed_ranks.get(name),
        )
        proprietary.append(enriched)
    proprietary.sort(key=lambda item: (item.get("score_rank") or 10**9, item["engine"]))

    production = [
        item for item in summary
        if item.get("full_pass") and item.get("family") != "REFERENCE"
    ]
    top_ratio = sorted(production, key=lambda item: item.get("geomean_ratio", 0.0), reverse=True)[:10]
    top_score = sorted(production, key=lambda item: item.get("geomean_score", 0.0), reverse=True)[:10]
    top_balanced = sorted(production, key=lambda item: item.get("geomean_balanced_score", 0.0), reverse=True)[:10]

    # Research-only lower envelope: best already-produced verified archive per dataset.
    envelope = []
    for dataset in sorted({row.get("dataset") for row in rows}):
        passed = [
            row for row in rows
            if row.get("dataset") == dataset and row.get("status") == "PASS"
            and row.get("family") != "REFERENCE"
        ]
        if not passed:
            continue
        winner = min(passed, key=lambda row: int(row["compressed_bytes_median"]))
        envelope.append({
            "dataset": dataset,
            "engine": winner["engine"],
            "bytes": winner["compressed_bytes_median"],
            "original_bytes": winner["original_bytes"],
        })

    positions = {
        "system_count": report.get("system_count"),
        "dataset_count": report.get("dataset_count"),
        "row_count": report.get("row_count"),
        "pass_rows": report.get("pass_rows"),
        "proprietary": proprietary,
        "top_ratio": top_ratio,
        "top_score": top_score,
        "top_balanced": top_balanced,
        "verified_oracle_envelope": envelope,
    }
    (output / "UNIFIED_TIER1_POSITIONS.json").write_text(
        json.dumps(positions, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )

    def table(items: list[dict[str, Any]], metric: str, label: str) -> list[str]:
        lines = [f"## {label}", "", "| Rank | Engine | Family | Ratio | Encode ms | Score |", "|---:|---|---|---:|---:|---:|"]
        for index, item in enumerate(items, 1):
            lines.append(
                f"| {index} | {item['engine']} | {item['family']} | "
                f"{item.get('geomean_ratio', 0.0):.6f}× | {item.get('total_encode_ms', 0.0):.3f} | "
                f"{item.get(metric, 0.0):.6f} |"
            )
        lines.append("")
        return lines

    shtenco_top5_score = sum(
        str(item.get("engine", "")).startswith("SHTENCO") for item in top_score[:5]
    )
    shtenco_top5_ratio = sum(
        str(item.get("engine", "")).startswith("SHTENCO") for item in top_ratio[:5]
    )
    exact_ok = report.get("pass_rows") == report.get("row_count")

    lines = [
        "# SHTENCO Unified Tier-1 Benchmark",
        "",
        f"- Systems: **{report.get('system_count')}**",
        f"- Datasets: **{report.get('dataset_count')}**",
        f"- Rows: **{report.get('row_count')}**",
        f"- Exact PASS: **{report.get('pass_rows')}/{report.get('row_count')}**",
        f"- SHTENCO systems in score TOP-5: **{shtenco_top5_score}**",
        f"- SHTENCO systems in ratio TOP-5: **{shtenco_top5_ratio}**",
        "",
        "The verified oracle envelope below is a research lower bound assembled from existing rows; it is not ranked as a deployable compressor.",
        "",
    ]
    lines += table(top_ratio, "geomean_ratio", "TOP-10 by compression ratio")
    lines += table(top_score, "geomean_score", "TOP-10 by ratio / encode-time score")
    lines += table(top_balanced, "geomean_balanced_score", "TOP-10 by balanced score")
    lines += [
        "## SHTENCO positions",
        "",
        "| Engine | Ratio rank | Score rank | Balanced rank | Speed rank | Full pass |",
        "|---|---:|---:|---:|---:|:---:|",
    ]
    for item in proprietary:
        lines.append(
            f"| {item['engine']} | {item.get('ratio_rank') or '—'} | {item.get('score_rank') or '—'} | "
            f"{item.get('balanced_rank') or '—'} | {item.get('speed_rank') or '—'} | "
            f"{'yes' if item.get('full_pass') else 'no'} |"
        )
    lines += [
        "",
        "## Verified oracle envelope (not a ranked compressor)",
        "",
        "| Dataset | Best verified engine | Bytes | Original |",
        "|---|---|---:|---:|",
    ]
    for item in envelope:
        lines.append(f"| {item['dataset']} | {item['engine']} | {item['bytes']} | {item['original_bytes']} |")
    lines += [
        "",
        "## Acceptance",
        "",
        f"- All rows exact: **{'PASS' if exact_ok else 'FAIL'}**",
        f"- At least one SHTENCO score TOP-5: **{'PASS' if shtenco_top5_score >= 1 else 'FAIL'}**",
        f"- At least one SHTENCO ratio TOP-5: **{'PASS' if shtenco_top5_ratio >= 1 else 'FAIL'}**",
        "",
    ]
    (output / "UNIFIED_TIER1_FINDINGS.md").write_text("\n".join(lines), encoding="utf-8")


benchmark.build_systems = build_unified_systems


def main() -> None:
    output = _output_path(sys.argv[1:])
    benchmark.main()
    _write_unified_findings(output)


if __name__ == "__main__":
    main()
