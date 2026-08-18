#!/usr/bin/env python3
"""Scoped content-addressed deduplication evidence for SYNERGY storage.

Public/opt-in data may share one global dedup domain. Private data is domain
separated by tenant so an unrelated tenant cannot probe whether identical
private content already exists. This module stores only commitments/byte counts;
actual encrypted chunk placement belongs to the storage provider layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib


class DedupScope(StrEnum):
    PUBLIC = "public"
    TENANT_PRIVATE = "tenant_private"


@dataclass(frozen=True, slots=True)
class ChunkEvidence:
    chunk_id: str
    archive_bytes: int


@dataclass(frozen=True, slots=True)
class ContentManifest:
    content_id: str
    scope: DedupScope
    domain_id: str
    logical_archive_bytes: int
    chunks: tuple[ChunkEvidence, ...]


@dataclass(frozen=True, slots=True)
class DedupReceipt:
    content_id: str
    logical_archive_bytes: int
    newly_stored_unique_bytes: int
    reused_bytes: int
    cumulative_logical_bytes: int
    cumulative_unique_bytes: int
    cumulative_dedup_factor: float
    catalog_root: str


def domain_tag(scope: DedupScope, tenant_id: str | None = None) -> str:
    if scope == DedupScope.PUBLIC:
        return "SYNERGIA:DEDUP:PUBLIC:V1"
    tenant = (tenant_id or "").strip()
    if not tenant:
        raise ValueError("tenant_id required for private dedup scope")
    return "SYNERGIA:DEDUP:TENANT:V1:" + hashlib.sha256(tenant.encode()).hexdigest()


def chunk_commitment(data: bytes, *, scope: DedupScope, tenant_id: str | None = None) -> str:
    tag = domain_tag(scope, tenant_id)
    return hashlib.sha256(tag.encode() + b"\x00" + bytes(data)).hexdigest()


class DedupCatalog:
    def __init__(self) -> None:
        self._chunk_sizes: dict[tuple[str, str], int] = {}
        self._content_ids: set[str] = set()
        self._logical_bytes = 0

    @property
    def unique_bytes(self) -> int:
        return sum(self._chunk_sizes.values())

    @property
    def logical_bytes(self) -> int:
        return self._logical_bytes

    def add(self, manifest: ContentManifest) -> DedupReceipt:
        if manifest.content_id in self._content_ids:
            raise ValueError("duplicate content_id")
        if manifest.logical_archive_bytes <= 0:
            raise ValueError("logical_archive_bytes must be positive")
        if not manifest.chunks:
            raise ValueError("content manifest requires chunks")
        if sum(chunk.archive_bytes for chunk in manifest.chunks) != manifest.logical_archive_bytes:
            raise ValueError("chunk byte sum must equal logical archive bytes")
        if any(chunk.archive_bytes <= 0 or not chunk.chunk_id for chunk in manifest.chunks):
            raise ValueError("invalid chunk evidence")

        before_unique = self.unique_bytes
        for chunk in manifest.chunks:
            key = (manifest.domain_id, chunk.chunk_id)
            previous = self._chunk_sizes.get(key)
            if previous is None:
                self._chunk_sizes[key] = chunk.archive_bytes
            elif previous != chunk.archive_bytes:
                raise ValueError("same chunk commitment has conflicting size")
        self._content_ids.add(manifest.content_id)
        self._logical_bytes += manifest.logical_archive_bytes
        after_unique = self.unique_bytes
        newly = after_unique - before_unique
        reused = manifest.logical_archive_bytes - newly
        factor = self.logical_bytes / after_unique if after_unique else float("inf")
        return DedupReceipt(
            content_id=manifest.content_id,
            logical_archive_bytes=manifest.logical_archive_bytes,
            newly_stored_unique_bytes=newly,
            reused_bytes=reused,
            cumulative_logical_bytes=self.logical_bytes,
            cumulative_unique_bytes=after_unique,
            cumulative_dedup_factor=factor,
            catalog_root=self.catalog_root(),
        )

    def catalog_root(self) -> str:
        h = hashlib.sha256(b"SYNERGIA:DEDUP:CATALOG:V1")
        for (domain, chunk_id), size in sorted(self._chunk_sizes.items()):
            h.update(domain.encode())
            h.update(b"\x00")
            h.update(chunk_id.encode())
            h.update(b"\x00")
            h.update(str(size).encode())
            h.update(b"\n")
        return h.hexdigest()
