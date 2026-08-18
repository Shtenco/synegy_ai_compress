import json
from datetime import UTC, datetime
from pathlib import Path

from sinergy_archive import ArchiveEntry, ArchiveManifest


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/archive_manifest_v1.schema.json"


def _payload() -> dict:
    manifest = ArchiveManifest(
        snapshot_id="snapshot-001",
        source_repository="Shtenco/cashero",
        source_ref="main",
        source_commit="a" * 40,
        created_at=datetime(2026, 8, 18, 19, 0, tzinfo=UTC),
        purpose="LEGACY_PROVENANCE",
        entries=(ArchiveEntry("README.md", 7, "b" * 64, "text/markdown"),),
    )
    return manifest.to_dict()


def test_runtime_emits_exact_declared_top_level_shape() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    payload = _payload()
    assert set(payload) == set(schema["required"])
    assert set(payload) <= set(schema["properties"])
    assert payload["schema"] == "archive.manifest/v1"


def test_runtime_entry_shape_matches_schema() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    entry_schema = schema["properties"]["entries"]["items"]
    entry = _payload()["entries"][0]
    assert set(entry) == set(entry_schema["required"])
    assert set(entry) <= set(entry_schema["properties"])


def test_archive_authority_is_schema_locked() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["properties"]["immutable"] == {"const": True}
    assert schema["properties"]["authority"] == {"const": "ARCHIVE_ONLY"}
