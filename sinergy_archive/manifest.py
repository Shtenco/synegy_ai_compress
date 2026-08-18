from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Iterable


SCHEMA = "archive.manifest/v1"
HEX = frozenset("0123456789abcdef")
MAX_SAFE_JSON_INTEGER = 9_007_199_254_740_991
ALLOWED_PURPOSES = frozenset(
    {
        "LEGACY_PROVENANCE",
        "REPRODUCIBILITY",
        "BENCHMARK_EVIDENCE",
        "RELEASE_SNAPSHOT",
        "MIGRATION_BASELINE",
    }
)


class ArchiveManifestError(ValueError):
    """Raised when an archive manifest is incomplete or ambiguous."""


def _text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ArchiveManifestError(f"{field_name} must be text")
    result = value.strip()
    if not result:
        raise ArchiveManifestError(f"{field_name} is required")
    return result


def _hex(value: str, length: int, field_name: str) -> str:
    result = _text(value, field_name).lower()
    if len(result) != length or any(c not in HEX for c in result):
        raise ArchiveManifestError(
            f"{field_name} must be a {length}-character hexadecimal digest"
        )
    return result


def _canonical_json(payload: object) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class ArchiveEntry:
    path: str
    size_bytes: int
    sha256: str
    media_type: str = "application/octet-stream"

    def __post_init__(self) -> None:
        path = _text(self.path, "path").replace("\\", "/")
        if path.startswith("/") or path in {".", ".."} or any(
            part in {"", ".", ".."} for part in path.split("/")
        ):
            raise ArchiveManifestError("path must be a normalized relative path")
        if isinstance(self.size_bytes, bool) or not isinstance(self.size_bytes, int):
            raise ArchiveManifestError("size_bytes must be an integer")
        if not 0 <= self.size_bytes <= MAX_SAFE_JSON_INTEGER:
            raise ArchiveManifestError(
                "size_bytes must be a non-negative cross-language safe integer"
            )
        media_type = _text(self.media_type, "media_type")
        object.__setattr__(self, "path", path)
        object.__setattr__(self, "sha256", _hex(self.sha256, 64, "sha256"))
        object.__setattr__(self, "media_type", media_type)

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
            "media_type": self.media_type,
        }


@dataclass(frozen=True)
class ArchiveManifest:
    snapshot_id: str
    source_repository: str
    source_ref: str
    source_commit: str
    created_at: datetime
    purpose: str
    entries: tuple[ArchiveEntry, ...]
    immutable: bool = True
    authority: str = "ARCHIVE_ONLY"
    compression_codec: str | None = None
    compressed_artifact_sha256: str | None = None

    def __post_init__(self) -> None:
        snapshot_id = _text(self.snapshot_id, "snapshot_id")
        source_repository = _text(self.source_repository, "source_repository")
        if source_repository.count("/") != 1:
            raise ArchiveManifestError("source_repository must use owner/repository form")
        source_ref = _text(self.source_ref, "source_ref")
        source_commit = _hex(self.source_commit, 40, "source_commit")
        if not isinstance(self.created_at, datetime):
            raise ArchiveManifestError("created_at must be datetime")
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ArchiveManifestError("created_at must be timezone-aware")
        purpose = _text(self.purpose, "purpose").upper()
        if purpose not in ALLOWED_PURPOSES:
            raise ArchiveManifestError(f"unsupported archive purpose: {purpose}")
        if self.immutable is not True:
            raise ArchiveManifestError("archive manifest must be immutable")
        if self.authority != "ARCHIVE_ONLY":
            raise ArchiveManifestError(
                "archive/compression metadata cannot claim financial or model authority"
            )
        entries = tuple(self.entries)
        if not entries:
            raise ArchiveManifestError("archive must contain at least one entry")
        if any(not isinstance(item, ArchiveEntry) for item in entries):
            raise ArchiveManifestError("entries must contain ArchiveEntry values")
        paths = [item.path for item in entries]
        if len(paths) != len(set(paths)):
            raise ArchiveManifestError("archive entry paths must be unique")
        entries = tuple(sorted(entries, key=lambda item: item.path))
        if len(entries) > MAX_SAFE_JSON_INTEGER:
            raise ArchiveManifestError("entry_count exceeds cross-language safe range")
        total_bytes = sum(item.size_bytes for item in entries)
        if total_bytes > MAX_SAFE_JSON_INTEGER:
            raise ArchiveManifestError(
                "total_uncompressed_bytes exceeds cross-language safe range"
            )

        codec = self.compression_codec
        artifact_digest = self.compressed_artifact_sha256
        if codec is None and artifact_digest is not None:
            raise ArchiveManifestError(
                "compressed_artifact_sha256 requires compression_codec"
            )
        if codec is not None:
            codec = _text(codec, "compression_codec")
            if artifact_digest is None:
                raise ArchiveManifestError(
                    "compression_codec requires compressed_artifact_sha256"
                )
            artifact_digest = _hex(
                artifact_digest, 64, "compressed_artifact_sha256"
            )

        object.__setattr__(self, "snapshot_id", snapshot_id)
        object.__setattr__(self, "source_repository", source_repository)
        object.__setattr__(self, "source_ref", source_ref)
        object.__setattr__(self, "source_commit", source_commit)
        object.__setattr__(self, "created_at", self.created_at.astimezone(UTC))
        object.__setattr__(self, "purpose", purpose)
        object.__setattr__(self, "entries", entries)
        object.__setattr__(self, "compression_codec", codec)
        object.__setattr__(self, "compressed_artifact_sha256", artifact_digest)

    @property
    def total_uncompressed_bytes(self) -> int:
        return sum(item.size_bytes for item in self.entries)

    @property
    def source_tree_digest(self) -> str:
        payload = [item.to_dict() for item in self.entries]
        return hashlib.sha256(_canonical_json(payload)).hexdigest()

    def to_dict(self, *, include_manifest_digest: bool = True) -> dict[str, object]:
        payload: dict[str, object] = {
            "schema": SCHEMA,
            "snapshot_id": self.snapshot_id,
            "source_repository": self.source_repository,
            "source_ref": self.source_ref,
            "source_commit": self.source_commit,
            "created_at": self.created_at.isoformat().replace("+00:00", "Z"),
            "purpose": self.purpose,
            "immutable": self.immutable,
            "authority": self.authority,
            "entries": [item.to_dict() for item in self.entries],
            "entry_count": len(self.entries),
            "total_uncompressed_bytes": self.total_uncompressed_bytes,
            "source_tree_digest": self.source_tree_digest,
            "compression_codec": self.compression_codec,
            "compressed_artifact_sha256": self.compressed_artifact_sha256,
        }
        if include_manifest_digest:
            payload["manifest_digest"] = manifest_digest(self)
        return payload


def manifest_digest(manifest: ArchiveManifest) -> str:
    return hashlib.sha256(
        _canonical_json(manifest.to_dict(include_manifest_digest=False))
    ).hexdigest()


def verify_manifest_entries(
    manifest: ArchiveManifest,
    observed: Iterable[tuple[str, int, str]],
) -> None:
    """Verify path/size/content digests without invoking any compression codec."""

    expected = {
        item.path: (item.size_bytes, item.sha256) for item in manifest.entries
    }
    actual: dict[str, tuple[int, str]] = {}
    for path, size_bytes, sha256 in observed:
        entry = ArchiveEntry(path=path, size_bytes=size_bytes, sha256=sha256)
        if entry.path in actual:
            raise ArchiveManifestError("observed paths must be unique")
        actual[entry.path] = (entry.size_bytes, entry.sha256)
    if actual != expected:
        raise ArchiveManifestError("observed source files do not match archive manifest")
