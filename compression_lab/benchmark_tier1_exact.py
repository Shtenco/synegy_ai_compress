#!/usr/bin/env python3
"""Run the unchanged exact benchmark with SHTENCO Tier-1 engines appended."""
from __future__ import annotations
import benchmark_all_systems_exact as benchmark
from shtenco_tier1_engines import tier1_engine_suite

_original_build_systems = benchmark.build_systems


def build_systems_with_tier1():
    systems = _original_build_systems()
    seen = {item.name for item in systems}
    for name, family, engine in tier1_engine_suite():
        if name not in seen:
            systems.append(benchmark.SystemSpec(name, family, engine))
            seen.add(name)
    return systems


benchmark.build_systems = build_systems_with_tier1

if __name__ == "__main__":
    benchmark.main()
