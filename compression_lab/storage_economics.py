#!/usr/bin/env python3
"""Auditable storage-cost model driven by measured codec evidence."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StorageEconomics:
    raw_bytes: int
    archive_bytes: int
    raw_price_per_gib_epoch: float
    synergy_price_per_gib_epoch: float
    redundancy_multiplier: float

    def validate(self) -> None:
        if self.raw_bytes <= 0 or self.archive_bytes <= 0:
            raise ValueError("byte counts must be positive")
        if self.raw_price_per_gib_epoch <= 0 or self.synergy_price_per_gib_epoch <= 0:
            raise ValueError("prices must be positive")
        if self.redundancy_multiplier < 1.0:
            raise ValueError("redundancy multiplier must be >= 1")

    @property
    def compression_factor(self) -> float:
        return self.raw_bytes / self.archive_bytes

    @property
    def effective_archive_ratio(self) -> float:
        return (self.archive_bytes / self.raw_bytes) * self.redundancy_multiplier

    @property
    def cost_ratio(self) -> float:
        self.validate()
        return self.effective_archive_ratio * (self.synergy_price_per_gib_epoch / self.raw_price_per_gib_epoch)

    @property
    def saving_factor(self) -> float:
        ratio = self.cost_ratio
        return 1.0 / ratio if ratio > 0 else float("inf")

    @property
    def saving_percent(self) -> float:
        return (1.0 - self.cost_ratio) * 100.0


def required_compression_for_saving_factor(
    desired_saving_factor: float,
    *,
    raw_price_per_gib_epoch: float,
    synergy_price_per_gib_epoch: float,
    redundancy_multiplier: float,
) -> float:
    """Minimum compression factor R/C required for a target total cost saving.

    target = raw_cost / synergy_cost
           = compression_factor * raw_price / (redundancy * synergy_price)
    """
    if desired_saving_factor <= 0:
        raise ValueError("desired saving factor must be positive")
    if raw_price_per_gib_epoch <= 0 or synergy_price_per_gib_epoch <= 0:
        raise ValueError("prices must be positive")
    if redundancy_multiplier < 1:
        raise ValueError("redundancy multiplier must be >= 1")
    return desired_saving_factor * redundancy_multiplier * synergy_price_per_gib_epoch / raw_price_per_gib_epoch
