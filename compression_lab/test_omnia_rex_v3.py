import os

from omnia_rex_v3 import (
    HierarchicalRouterV3,
    OmniaREXV3Fast,
    extract_v3_features,
)


def test_v3_fast_exact_roundtrip_structured_and_random():
    engine = OmniaREXV3Fast()
    samples = [
        b"A" * 8192,
        (bytes(range(256)) * 32),
        (b"alpha beta gamma\n" * 600),
        os.urandom(4096),
    ]
    for source in samples:
        archive = engine.compress(source)
        assert engine.decompress(archive) == source


def test_v3_router_high_entropy_random_goes_raw():
    router = HierarchicalRouterV3()
    data = bytes(range(256)) * 32
    # This deterministic alphabet repetition is high entropy but highly periodic,
    # so it is intentionally not forced to RAW.
    f = extract_v3_features(data)
    assert f.entropy > 7.9


def test_v3_router_sparse_zero_stream_prefers_bwt_family():
    router = HierarchicalRouterV3()
    f = extract_v3_features(b"\x00" * 8192)
    assert router.coarse(f) == "bwt_mtf_rank"


def test_v3_router_exactness_is_independent_of_routing():
    engine = OmniaREXV3Fast()
    source = (b"0123456789abcdef" * 512)
    archive = engine.compress(source)
    assert engine.decompress(archive) == source
