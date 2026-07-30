import hashlib
from pathlib import Path

from compression_lab.benchmark_gabriel_corpus import (
    _query_ranges,
    _run_worker,
    built_in_corpus,
    engine_specs,
)


def test_builtin_corpus_is_deterministic():
    first = built_in_corpus(4096)
    second = built_in_corpus(4096)
    assert len(first) == 7
    assert [item.name for item in first] == [item.name for item in second]
    assert all(len(item.data) == 4096 for item in first)
    assert [hashlib.sha256(item.data).digest() for item in first] == [
        hashlib.sha256(item.data).digest() for item in second
    ]
    assert first[-1].kind == "high_entropy"


def test_query_ranges_are_valid_and_repeatable():
    first = _query_ranges(8192, 7, 1024)
    assert first == _query_ranges(8192, 7, 1024)
    assert len(first) == 7
    assert all(0 <= start < end <= 8192 and end - start == 1024 for start, end in first)


def test_raw_worker_roundtrip_and_range(tmp_path: Path):
    source = built_in_corpus(2048)[0].data
    path = tmp_path / "source.bin"
    path.write_bytes(source)
    row = _run_worker("raw", path, random_queries=3, random_bytes=256)
    assert row.status == "PASS"
    assert row.input_bytes == row.archive_bytes == len(source)
    assert row.sha256 == hashlib.sha256(source).hexdigest()
    assert row.logical_bytes_inflated == len(source) * 3


def test_required_public_engines_are_registered():
    specs = engine_specs()
    assert {"raw", "gabriel-max", "zstd-19", "brotli-11", "graal-igc"} <= set(specs)
    # UMC-256 is intentionally conditional: only the exact historical module qualifies.
