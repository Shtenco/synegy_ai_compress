from omnia_rex_router_v2 import ExtraTreesCostRouter, extract_features
from omnia_rex_v2 import QTD3SharedLayer


def test_shared_break_even_math():
    assert QTD3SharedLayer.break_even_reuses(1000, 100, 300) == 5
    assert QTD3SharedLayer.break_even_reuses(1000, 300, 300) is None
    assert QTD3SharedLayer.break_even_reuses(0, 100, 300) == 1


def test_router_guards_random():
    f = {
        "entropy": 7.99,
        "repeat16": 0.0,
        "lag256_equal": 0.0,
        "zero": 0.0,
    }
    assert "raw" in ExtraTreesCostRouter.guard_families(f)


def test_router_guards_sparse():
    f = {
        "entropy": 0.2,
        "repeat16": 0.8,
        "lag256_equal": 0.9,
        "zero": 0.99,
    }
    assert "bwt_mtf_rank" in ExtraTreesCostRouter.guard_families(f)


def test_feature_extraction_is_finite():
    f = extract_features((b"abc123\n" * 1000)[:4096])
    assert set(f)
    assert 0.0 <= f["zero"] <= 1.0
    assert 0.0 <= f["repeat16"] <= 1.0
    assert f["entropy"] >= 0.0
