from datetime import UTC, datetime

import pytest

from sinergy_archive import (
    ArchiveEntry,
    ArchiveManifest,
    ArchiveManifestError,
    manifest_digest,
)
from sinergy_archive.manifest import verify_manifest_entries


def _manifest(**changes) -> ArchiveManifest:
    kwargs = {
        "snapshot_id": "snapshot-financial-os-001",
        "source_repository": "Shtenco/ai_financial_system",
        "source_ref": "feat/financial-os-v4-20260809",
        "source_commit": "a" * 40,
        "created_at": datetime(2026, 8, 18, 19, 0, tzinfo=UTC),
        "purpose": "LEGACY_PROVENANCE",
        "entries": (
            ArchiveEntry("README.md", 10, "b" * 64, "text/markdown"),
            ArchiveEntry("src/core.py", 20, "c" * 64, "text/x-python"),
        ),
    }
    kwargs.update(changes)
    return ArchiveManifest(**kwargs)


def test_manifest_is_deterministic_and_entry_order_independent() -> None:
    first = _manifest()
    second = _manifest(entries=tuple(reversed(first.entries)))
    assert first.to_dict() == second.to_dict()
    assert manifest_digest(first) == manifest_digest(second)


def test_source_tree_identity_is_independent_of_compression_codec() -> None:
    raw = _manifest()
    compressed = _manifest(
        compression_codec="OMNIA-V2",
        compressed_artifact_sha256="d" * 64,
    )
    assert raw.source_tree_digest == compressed.source_tree_digest
    assert raw.to_dict()["entries"] == compressed.to_dict()["entries"]
    assert raw.to_dict()["manifest_digest"] != compressed.to_dict()["manifest_digest"]


def test_archive_cannot_claim_financial_or_model_authority() -> None:
    with pytest.raises(ArchiveManifestError):
        _manifest(authority="FINANCIAL_OS")


def test_archive_must_be_immutable() -> None:
    with pytest.raises(ArchiveManifestError):
        _manifest(immutable=False)


def test_duplicate_or_unsafe_paths_fail_closed() -> None:
    duplicate = ArchiveEntry("x.txt", 1, "a" * 64)
    with pytest.raises(ArchiveManifestError):
        _manifest(entries=(duplicate, duplicate))
    with pytest.raises(ArchiveManifestError):
        ArchiveEntry("../secret", 1, "a" * 64)
    with pytest.raises(ArchiveManifestError):
        ArchiveEntry("/absolute", 1, "a" * 64)


def test_sizes_use_cross_language_safe_integer_range() -> None:
    with pytest.raises(ArchiveManifestError):
        ArchiveEntry("huge.bin", 9_007_199_254_740_992, "a" * 64)
    with pytest.raises(ArchiveManifestError):
        ArchiveEntry("negative.bin", -1, "a" * 64)


def test_codec_and_compressed_artifact_digest_are_bound_together() -> None:
    with pytest.raises(ArchiveManifestError):
        _manifest(compression_codec="OMNIA-V2")
    with pytest.raises(ArchiveManifestError):
        _manifest(compressed_artifact_sha256="d" * 64)


def test_verify_manifest_entries_checks_original_file_identity_not_codec() -> None:
    manifest = _manifest(compression_codec="OMNIA-V2", compressed_artifact_sha256="d" * 64)
    verify_manifest_entries(
        manifest,
        [
            ("src/core.py", 20, "c" * 64),
            ("README.md", 10, "b" * 64),
        ],
    )
    with pytest.raises(ArchiveManifestError):
        verify_manifest_entries(
            manifest,
            [
                ("src/core.py", 20, "e" * 64),
                ("README.md", 10, "b" * 64),
            ],
        )


def test_created_at_must_be_timezone_aware() -> None:
    with pytest.raises(ArchiveManifestError):
        _manifest(created_at=datetime(2026, 8, 18, 19, 0))
