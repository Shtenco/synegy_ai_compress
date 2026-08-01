#!/usr/bin/env python3
"""Federated 81-system benchmark: frozen 69 + active Tier-1 + Math v3.

This adapter deliberately reuses the exact historical corpus, report schema and
ranking implementation from ``benchmark_unified_tier1.py``.  It only extends the
active engine inventory and marks the expensive mathematical MAX portfolios as
single-exact measurements, matching the existing heavy-profile protocol.
"""
from __future__ import annotations

import statistics

import benchmark_unified_tier1 as base
from shtenco_math_portfolio_v3 import math_v3_engine_suite


HEAVY_MATH_ENGINES = {
    "SHTENCO MATH PORTFOLIO V3 MAX",
    "SHTENCO OMNIA-MATH V3 MAX",
}


def systems():
    """Return unique active systems, including all five Math v3 profiles."""
    out = []
    seen = set()
    for suite in (
        base.tier1_engine_suite(),
        base.tier1_v21_engine_suite(),
        math_v3_engine_suite(),
    ):
        for name, family, engine in suite:
            if name not in seen:
                out.append((name, family, engine))
                seen.add(name)
    return out


def one(name, family, engine, dataset, data, repeats):
    """Use the original protocol except for expensive Math MAX profiles."""
    if name not in HEAVY_MATH_ENGINES:
        return base.one(name, family, engine, dataset, data, repeats)

    digest = base._sha(data)
    try:
        enc = []
        dec = []
        sizes = []
        hashes = []
        modes = []
        archive, encode_ms = base._timed(engine.compress, data)
        restored, decode_ms = base._timed(engine.decompress, archive)
        if restored != data or base._sha(restored) != digest:
            raise ValueError("single-exact Math MAX verification failure")
        enc.append(encode_ms)
        dec.append(decode_ms)
        sizes.append(len(archive))
        hashes.append(base._sha(archive))
        modes.append(str(getattr(engine, "last_mode", "native")))
        size = int(statistics.median(sizes))
        encode_median = statistics.median(enc)
        decode_median = statistics.median(dec)
        ratio = len(data) / max(1, size)
        return {
            "dataset": dataset,
            "engine": name,
            "family": family,
            "status": "PASS",
            "sha256": "PASS",
            "original_bytes": len(data),
            "compressed_bytes_median": size,
            "compressed_bytes_min": min(sizes),
            "compressed_bytes_max": max(sizes),
            "ratio": ratio,
            "encode_ms_median": encode_median,
            "decode_ms_median": decode_median,
            "encode_mib_s": (len(data) / base.MIB) / max(encode_median / 1000, 1e-12),
            "decode_mib_s": (len(data) / base.MIB) / max(decode_median / 1000, 1e-12),
            "score_ratio_per_ms": ratio / max(encode_median, 0.001),
            "balanced_score": ratio / max((encode_median * decode_median) ** 0.5, 0.001),
            "archive_deterministic": len(set(hashes)) == 1,
            "archive_variation_bytes": max(sizes) - min(sizes),
            "mode": statistics.mode(modes),
            "repeats": 1,
            "timing_protocol": "single-exact",
            "measurement_run": "current",
        }
    except Exception as exc:
        return {
            "dataset": dataset,
            "engine": name,
            "family": family,
            "status": "FAIL",
            "sha256": "FAIL",
            "original_bytes": len(data),
            "compressed_bytes_median": None,
            "ratio": 0.0,
            "encode_ms_median": None,
            "decode_ms_median": None,
            "score_ratio_per_ms": 0.0,
            "balanced_score": 0.0,
            "archive_deterministic": False,
            "mode": "—",
            "repeats": 1,
            "timing_protocol": "single-exact",
            "measurement_run": "current",
            "error": f"{type(exc).__name__}: {exc}",
        }


# Patch only the two extension points used dynamically by base.main().
base.systems = systems
base.one = one


if __name__ == "__main__":
    base.main()
