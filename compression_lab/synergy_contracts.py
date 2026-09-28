from __future__ import annotations

from hashlib import sha256
from typing import Any


CONTRACT_ID = "synergy.archive.evidence/v1"
AUTHORITY = "compression_identity"


def archive_evidence_payload(
    *,
    source: bytes,
    archive: bytes,
    restored: bytes,
    codec_id: str,
    benchmark_id: str | None = None,
    random_access_supported: bool = False,
) -> dict[str, Any]:
    if restored != source:
        raise ValueError("lossless archive evidence requires exact byte round-trip")
    if not codec_id:
        raise ValueError("codec_id required")
    return {
        "source_sha256": sha256(source).hexdigest(),
        "archive_sha256": sha256(archive).hexdigest(),
        "codec_id": codec_id,
        "original_bytes": len(source),
        "archive_bytes": len(archive),
        "round_trip_verified": True,
        "benchmark_id": benchmark_id,
        "random_access_supported": bool(random_access_supported),
    }
