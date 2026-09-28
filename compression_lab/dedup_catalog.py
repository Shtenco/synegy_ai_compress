#!/usr/bin/env python3
"""Scoped content-addressed deduplication evidence for SYNERGY storage.

Public/opt-in data may share a global content-addressed domain. Private dedup uses
a tenant-managed secret key: chunk identifiers are HMAC-SHA256 values, not a
public hash of tenant id + plaintext. The chain/provider can commit the dedup
domain and byte accounting without learning the secret.

This reduces cross-tenant confirmation attacks. It does not hide object sizes,
access timing or every storage-side metadata channel; those require encryption,
padding and provider-access policy at higher layers.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import hmac


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


PUBLIC_DOMAIN = "SYNERGIA:DEDUP:PUBLIC:V2"
PRIVATE_DOMAIN_PREFIX = b"SYNERGIA:DEDUP:TENANT-DOMAIN:V2\x00"
PRIVATE_CHUNK_PREFIX = b"SYNERGIA:DEDUP:TENANT-CHUNK:V2\x00"


def _private_key(tenant_dedup_key: bytes | bytearray | memoryview | None) -> bytes:
    if tenant_dedup_key is None:
        raise ValueError("tenant_dedup_key required for private dedup scope")
    key = bytes(tenant_dedup_key)
    if len(key) < 16:
        raise ValueError("tenant_dedup_key must contain at least 128 bits")
    return key


def private_domain_id(tenant_dedup_key: bytes | bytearray | memoryview) -> str:
    key = _private_key(tenant_dedup_key)
    # This is a commitment/domain label, not the secret itself.
    return hashlib.sha256(PRIVATE_DOMAIN_PREFIX + key).hexdigest()


def domain_tag(
    scope: DedupScope,
    tenant_dedup_key: bytes | bytearray | memoryview | None = None,
) -> str:
    if scope == DedupScope.PUBLIC:
        return PUBLIC_DOMAIN
    return "SYNERGIA:DEDUP:TENANT:V2:" + private_domain_id(_private_key(tenant_dedup_key))


def chunk_commitment(
    data: bytes,
    *,
    scope: DedupScope,
    tenant_dedup_key: bytes | bytearray | memoryview | None = None,
) -> str:
    payload = bytes(data)
    if scope == DedupScope.PUBLIC:
        return hashlib.sha256(PUBLIC_DOMAIN.encode() + b"\x00" + payload).hexdigest()
    key = _private_key(tenant_dedup_key)
    return hmac.new(key, PRIVATE_CHUNK_PREFIX + payload, hashlib.sha256).hexdigest()


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
        if not manifest.domain_id:
            raise ValueError("dedup domain commitment required")
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
        h = hashlib.sha256(b"SYNERGIA:DEDUP:CATALOG:V2")
        for (domain, chunk_id), size in sorted(self._chunk_sizes.items()):
            h.update(domain.encode())
            h.update(b"\x00")
            h.update(chunk_id.encode())
            h.update(b"\x00")
            h.update(str(size).encode())
            h.update(b"\n")
        return h.hexdigest()
