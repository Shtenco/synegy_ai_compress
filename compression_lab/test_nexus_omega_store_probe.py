from __future__ import annotations

from .nexus_omega_store_probe import probe_bytes, synthetic_corpus


def test_synthetic_corpus_is_deterministic() -> None:
    a = synthetic_corpus(4096, seed=7)
    b = synthetic_corpus(4096, seed=7)
    assert a == b
    assert set(a) == {
        "binary-50-50-packed",
        "binary-10pct-ones",
        "activation-mask-3pct",
        "ternary-60pct-zero-2bit",
        "binary-factor-correlated-rows",
    }
    assert all(len(payload) == 4096 for payload in a.values())


def test_raw_probe_is_exact_and_uncompressed() -> None:
    source = bytes(range(256)) * 8
    row = probe_bytes(
        "raw-control",
        source,
        block_bytes=256,
        profiles=["raw"],
        expected_read_bytes=64,
    )
    assert row.source_bytes == len(source)
    assert row.stored_bytes == len(source)
    assert row.ratio == 1.0
    assert row.tiles == 8
    assert row.route_counts == {"raw:RAW": 8}


def test_incompressible_control_never_forces_expansion() -> None:
    source = synthetic_corpus(8192, seed=11)["binary-50-50-packed"]
    row = probe_bytes(
        "random-control",
        source,
        block_bytes=4096,
        profiles=["raw", "omnia-speed"],
        expected_read_bytes=4096,
    )
    assert row.stored_bytes <= len(source)
