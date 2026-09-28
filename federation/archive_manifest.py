from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256


def sha256_hex(data: bytes) -> str:
    return sha256(data).hexdigest()


@dataclass(frozen=True)
class FederationArchiveManifest:
    object_id: str
    object_class: str
    producer_repo: str
    semantic_owner_repo: str
    canonical_content_sha256: str
    archive_sha256: str
    codec_id: str
    codec_version: str
    original_size: int
    archive_size: int
    storage_tier: str
    created_at: str
    dictionary_or_model_sha256: str | None = None
    schema: str = "synergy.archive-manifest/v1"
    archive_authority: str = "Shtenco/ai_compress"
    semantic_authority: str = "NONE"

    @classmethod
    def from_bytes(
        cls,
        *,
        object_id: str,
        object_class: str,
        producer_repo: str,
        semantic_owner_repo: str,
        canonical_bytes: bytes,
        archive_bytes: bytes,
        codec_id: str,
        codec_version: str,
        storage_tier: str,
        dictionary_or_model_sha256: str | None = None,
    ) -> "FederationArchiveManifest":
        return cls(
            object_id=object_id,
            object_class=object_class,
            producer_repo=producer_repo,
            semantic_owner_repo=semantic_owner_repo,
            canonical_content_sha256=sha256_hex(canonical_bytes),
            archive_sha256=sha256_hex(archive_bytes),
            codec_id=codec_id,
            codec_version=codec_version,
            original_size=len(canonical_bytes),
            archive_size=len(archive_bytes),
            storage_tier=storage_tier,
            created_at=datetime.now(timezone.utc).isoformat(),
            dictionary_or_model_sha256=dictionary_or_model_sha256,
        )

    def verify_archive(self, archive_bytes: bytes) -> bool:
        return sha256_hex(archive_bytes) == self.archive_sha256

    def verify_decoded(self, decoded_bytes: bytes) -> bool:
        return sha256_hex(decoded_bytes) == self.canonical_content_sha256

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
