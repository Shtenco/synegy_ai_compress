#!/usr/bin/env python3
"""End-to-end storage economics from measured byte evidence.

The model separates four independent multipliers:
1. lossless compression;
2. scoped content-addressed deduplication;
3. erasure/redundancy overhead;
4. provider price per physical GiB-epoch.

No fixed 1000x claim is assumed. A large saving factor is valid only when the
measured byte counts and actual provider prices imply it.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StorageStackEconomics:
    logical_raw_bytes: int
    logical_archive_bytes_before_dedup: int
    unique_archive_bytes_after_dedup: int
    erasure_k: int
    erasure_n: int
    conventional_price_per_gib_epoch: float
    synergy_price_per_gib_epoch: float

    def validate(self) -> None:
        if self.logical_raw_bytes <= 0:
            raise ValueError("logical_raw_bytes must be positive")
        if self.logical_archive_bytes_before_dedup <= 0:
            raise ValueError("logical archive bytes must be positive")
        if self.unique_archive_bytes_after_dedup <= 0:
            raise ValueError("unique archive bytes must be positive")
        if self.unique_archive_bytes_after_dedup > self.logical_archive_bytes_before_dedup:
            raise ValueError("unique archive bytes cannot exceed logical archive bytes")
        if not (0 < self.erasure_k <= self.erasure_n):
            raise ValueError("require 0 < erasure_k <= erasure_n")
        if self.conventional_price_per_gib_epoch <= 0 or self.synergy_price_per_gib_epoch <= 0:
            raise ValueError("storage prices must be positive")

    @property
    def compression_factor(self) -> float:
        self.validate()
        return self.logical_raw_bytes / self.logical_archive_bytes_before_dedup

    @property
    def dedup_factor(self) -> float:
        self.validate()
        return self.logical_archive_bytes_before_dedup / self.unique_archive_bytes_after_dedup

    @property
    def erasure_overhead(self) -> float:
        return self.erasure_n / self.erasure_k

    @property
    def price_advantage(self) -> float:
        return self.conventional_price_per_gib_epoch / self.synergy_price_per_gib_epoch

    @property
    def physical_synergy_bytes(self) -> float:
        self.validate()
        return self.unique_archive_bytes_after_dedup * self.erasure_overhead

    @property
    def saving_factor(self) -> float:
        self.validate()
        return (
            self.compression_factor
            * self.dedup_factor
            * self.price_advantage
            / self.erasure_overhead
        )

    def audit(self) -> dict[str, float | int | str]:
        return {
            "logical_raw_bytes": self.logical_raw_bytes,
            "logical_archive_bytes_before_dedup": self.logical_archive_bytes_before_dedup,
            "unique_archive_bytes_after_dedup": self.unique_archive_bytes_after_dedup,
            "compression_factor": self.compression_factor,
            "dedup_factor": self.dedup_factor,
            "erasure_overhead": self.erasure_overhead,
            "price_advantage": self.price_advantage,
            "physical_synergy_bytes": self.physical_synergy_bytes,
            "saving_factor": self.saving_factor,
            "claim_boundary": "DERIVED_FROM_MEASURED_BYTES_AND_ACTUAL_PRICES_ONLY",
        }


def required_price_advantage_for_target(
    target_saving_factor: float,
    *,
    compression_factor: float,
    dedup_factor: float,
    erasure_overhead: float,
) -> float:
    if min(target_saving_factor, compression_factor, dedup_factor, erasure_overhead) <= 0:
        raise ValueError("all factors must be positive")
    return target_saving_factor * erasure_overhead / (compression_factor * dedup_factor)
