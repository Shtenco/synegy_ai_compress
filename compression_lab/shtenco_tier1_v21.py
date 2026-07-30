#!/usr/bin/env python3
"""SHTENCO Tier-1 v2.1 production portfolio with evidence-gated MAX search."""
from __future__ import annotations
from shtenco_tier1_v2 import (
    ROUTE_BIP39_ZSTD3, ROUTE_GABRIEL_BALANCED, ROUTE_GABRIEL_MAX,
    ROUTE_RAW, ROUTE_TIER1_GRAAL, ROUTE_TIER1_NEXUS, ROUTE_TIER1_TSC,
    Features, GabrielHornBalancedTier1, GabrielHornRandomAccessTier1,
    GabrielHornSpeedTier1, OmniaTier1Balanced, OmniaTier1Max, OmniaTier1Speed,
)

class OmniaTier1V21Max(OmniaTier1Max):
    """Exhaustive mature-codec portfolio; Gabriel enters only with evidence."""
    name = "SHTENCO OMNIA TIER1 V2 MAX"
    def route_ids(self, source: bytes, features: Features) -> list[int]:
        routes = list(range(ROUTE_RAW, ROUTE_BIP39_ZSTD3 + 1))
        routes += [ROUTE_TIER1_GRAAL, ROUTE_TIER1_NEXUS, ROUTE_TIER1_TSC]
        structural = max(features.smooth, features.similar_blocks, features.atom_repeat, features.zero)
        if len(source) <= 131072 and structural >= 0.28:
            routes.append(ROUTE_GABRIEL_BALANCED)
        if len(source) <= 131072 and (features.smooth >= 0.48 or features.similar_blocks >= 0.58):
            routes.append(ROUTE_GABRIEL_MAX)
        return routes

def tier1_v21_engine_suite() -> list[tuple[str, str, object]]:
    engines = [OmniaTier1Speed(), OmniaTier1Balanced(), OmniaTier1V21Max(),
               GabrielHornSpeedTier1(), GabrielHornBalancedTier1(),
               GabrielHornRandomAccessTier1()]
    return [(engine.name, getattr(engine,"family","SHTENCO-TIER1-V2.1"), engine) for engine in engines]
