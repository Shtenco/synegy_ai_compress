"""Content-addressed archival primitives for the SINERGY repository federation."""

from .manifest import (
    ArchiveEntry,
    ArchiveManifest,
    ArchiveManifestError,
    manifest_digest,
)

__all__ = [
    "ArchiveEntry",
    "ArchiveManifest",
    "ArchiveManifestError",
    "manifest_digest",
]
