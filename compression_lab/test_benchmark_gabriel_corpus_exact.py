from compression_lab.benchmark_gabriel_corpus import Dataset, WorkerResult
from compression_lab.benchmark_gabriel_corpus_exact import _VARIABILITY, _median_row


def _result(size: int, encode_ns: int) -> WorkerResult:
    return WorkerResult(
        engine_id="legacy",
        engine="Legacy variable engine",
        family="TEST",
        native_random_access=False,
        input_bytes=1024,
        archive_bytes=size,
        encode_ns=encode_ns,
        decode_ns=1000,
        random_access_ns=2000,
        random_queries=2,
        requested_bytes=256,
        logical_bytes_inflated=2048,
        peak_rss_mib=20.0,
        sha256="a" * 64,
        status="PASS",
    )


def test_variable_archive_sizes_use_median_and_keep_span():
    _VARIABILITY.clear()
    dataset = Dataset("variable", b"x" * 1024, "test", "unit")
    row = _median_row(dataset, [_result(100, 10), _result(104, 20), _result(102, 30)])
    assert row.archive_bytes == 102
    assert row.ratio == 102 / 1024
    assert _VARIABILITY[-1]["archive_bytes_min"] == 100
    assert _VARIABILITY[-1]["archive_bytes_max"] == 104
    assert _VARIABILITY[-1]["archive_size_span"] == 4
