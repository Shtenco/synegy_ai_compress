from __future__ import annotations

from .dedup_catalog import (
    ChunkEvidence,
    ContentManifest,
    DedupCatalog,
    DedupScope,
    chunk_commitment,
    domain_tag,
)
from .storage_stack_economics import StorageStackEconomics, required_price_advantage_for_target


def manifest(content_id: str, domain: str, chunk_ids: list[str]) -> ContentManifest:
    chunks = tuple(ChunkEvidence(chunk_id=x, archive_bytes=100) for x in chunk_ids)
    return ContentManifest(
        content_id=content_id,
        scope=DedupScope.PUBLIC,
        domain_id=domain,
        logical_archive_bytes=100 * len(chunks),
        chunks=chunks,
    )


def test_public_identical_chunks_deduplicate_in_same_domain() -> None:
    catalog = DedupCatalog()
    first = catalog.add(manifest("a", domain_tag(DedupScope.PUBLIC), ["x", "y"]))
    second = catalog.add(manifest("b", domain_tag(DedupScope.PUBLIC), ["x", "z"]))
    assert first.newly_stored_unique_bytes == 200
    assert second.newly_stored_unique_bytes == 100
    assert second.reused_bytes == 100
    assert catalog.logical_bytes == 400
    assert catalog.unique_bytes == 300


def test_private_chunk_commitment_is_tenant_domain_separated() -> None:
    data = b"same private bytes"
    a = chunk_commitment(data, scope=DedupScope.TENANT_PRIVATE, tenant_id="company-a")
    b = chunk_commitment(data, scope=DedupScope.TENANT_PRIVATE, tenant_id="company-b")
    assert a != b


def test_end_to_end_saving_factor_is_product_of_measured_factors() -> None:
    economics = StorageStackEconomics(
        logical_raw_bytes=1_000_000,
        logical_archive_bytes_before_dedup=100_000,
        unique_archive_bytes_after_dedup=20_000,
        erasure_k=10,
        erasure_n=15,
        conventional_price_per_gib_epoch=10.0,
        synergy_price_per_gib_epoch=1.0,
    )
    # 10x compression * 5x dedup * 10x price advantage / 1.5 erasure overhead.
    assert abs(economics.saving_factor - (10 * 5 * 10 / 1.5)) < 1e-9


def test_target_thousand_x_is_a_requirement_not_a_constant() -> None:
    needed = required_price_advantage_for_target(
        1000.0,
        compression_factor=10.0,
        dedup_factor=20.0,
        erasure_overhead=1.5,
    )
    assert abs(needed - 7.5) < 1e-12
