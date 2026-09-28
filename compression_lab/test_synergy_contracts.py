import pytest

from compression_lab.synergy_contracts import CONTRACT_ID, archive_evidence_payload


def test_archive_evidence_requires_exact_round_trip():
    p=archive_evidence_payload(
        source=b"abc"*100,
        archive=b"compressed-demo",
        restored=b"abc"*100,
        codec_id="test-codec",
        benchmark_id="bench-1",
    )
    assert CONTRACT_ID=="synergy.archive.evidence/v1"
    assert p["round_trip_verified"] is True
    assert p["original_bytes"]==300


def test_archive_evidence_fails_on_loss():
    with pytest.raises(ValueError):
        archive_evidence_payload(
            source=b"abc",archive=b"x",restored=b"abd",codec_id="broken"
        )
