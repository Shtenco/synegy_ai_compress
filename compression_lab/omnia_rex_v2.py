from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

try:
    from .omnia_rex_v1 import OmniaREXV1
except ImportError:
    from omnia_rex_v1 import OmniaREXV1


@dataclass(frozen=True)
class SharedAccounting:
    target_bytes: int
    container_bytes: int
    model_bytes: int
    reuse_count: int
    amortized_bytes: float
    cold_total_bytes: int
    coverage_percent: float
    direct_baseline_bytes: int | None
    break_even_reuses_vs_direct: int | None
    exact_roundtrip: bool

    @property
    def amortized_ratio(self) -> float:
        return self.target_bytes / max(self.amortized_bytes, 1e-12)

    @property
    def transport_ratio(self) -> float:
        return self.target_bytes / max(self.container_bytes, 1)


class QTD3SharedLayer:
    """Honest adapter around qr_temporal.qtd3.

    The decoder is assumed to possess the exact shared model. The model is not
    free: model bytes, cold total, reuse count and amortized cost are always
    reported separately.
    """

    def __init__(self, model: Any, path: str, unix_ns: int) -> None:
        try:
            from qr_temporal.qtd3 import pack_blind_v3, unpack_v3, inspect_v3
        except Exception as exc:
            raise RuntimeError(
                "QTD3 requires the synergy_qr_compress qr_temporal package"
            ) from exc
        self.model = model
        self.path = str(path)
        self.unix_ns = int(unix_ns)
        self._pack = pack_blind_v3
        self._unpack = unpack_v3
        self._inspect = inspect_v3

    @staticmethod
    def break_even_reuses(
        model_bytes: int,
        shared_container_bytes: int,
        direct_bytes: int | None,
    ) -> int | None:
        if direct_bytes is None or direct_bytes <= shared_container_bytes:
            return None
        return max(1, math.ceil(model_bytes / (direct_bytes - shared_container_bytes)))

    def measure(
        self,
        target: bytes,
        *,
        reuse_count: int = 1,
        direct_baseline_bytes: int | None = None,
    ) -> SharedAccounting:
        if reuse_count < 1:
            raise ValueError("reuse_count must be >= 1")
        packed = self._pack(target, self.path, self.model, unix_ns=self.unix_ns)
        restored = self._unpack(packed.blob, self.model)
        exact = restored == target
        if not exact:
            raise ValueError("QTD3 exact round-trip failed")
        info = self._inspect(packed.blob, self.model)
        model_bytes = len(self.model.to_bytes())
        container_bytes = len(packed.blob)
        return SharedAccounting(
            target_bytes=len(target),
            container_bytes=container_bytes,
            model_bytes=model_bytes,
            reuse_count=reuse_count,
            amortized_bytes=container_bytes + model_bytes / reuse_count,
            cold_total_bytes=model_bytes + container_bytes,
            coverage_percent=float(info["model_coverage_percent"]),
            direct_baseline_bytes=direct_baseline_bytes,
            break_even_reuses_vs_direct=self.break_even_reuses(
                model_bytes, container_bytes, direct_baseline_bytes
            ),
            exact_roundtrip=True,
        )


@dataclass(frozen=True)
class V2Plan:
    mode: str
    standalone_bytes: int
    shared_transport_bytes: int | None
    shared_amortized_bytes: float | None
    chosen_effective_bytes: float
    reuse_count: int
    note: str


class OmniaREXV2:
    """V2 planner: standalone OMNIA-REX plus optional honest shared QTD3 layer."""

    name = "SHTENCO OMNIA-REX V2"
    family = "SHTENCO-OMNIA-REX"

    def __init__(self, standalone: OmniaREXV1 | None = None) -> None:
        self.standalone = standalone or OmniaREXV1()

    def compress_standalone(self, source: bytes) -> bytes:
        return self.standalone.compress(source)

    def decompress_standalone(self, archive: bytes) -> bytes:
        return self.standalone.decompress(archive)

    def select_plan(
        self,
        source: bytes,
        *,
        shared_layer: QTD3SharedLayer | None = None,
        reuse_count: int = 1,
    ) -> V2Plan:
        standalone = self.compress_standalone(source)
        if self.decompress_standalone(standalone) != source:
            raise ValueError("standalone verification failed")
        if shared_layer is None:
            return V2Plan(
                mode="standalone",
                standalone_bytes=len(standalone),
                shared_transport_bytes=None,
                shared_amortized_bytes=None,
                chosen_effective_bytes=float(len(standalone)),
                reuse_count=reuse_count,
                note="No shared model supplied.",
            )
        shared = shared_layer.measure(
            source,
            reuse_count=reuse_count,
            direct_baseline_bytes=len(standalone),
        )
        if shared.amortized_bytes < len(standalone):
            return V2Plan(
                mode="qtd3-shared",
                standalone_bytes=len(standalone),
                shared_transport_bytes=shared.container_bytes,
                shared_amortized_bytes=shared.amortized_bytes,
                chosen_effective_bytes=shared.amortized_bytes,
                reuse_count=reuse_count,
                note="Shared model cost is amortized, not hidden.",
            )
        return V2Plan(
            mode="standalone",
            standalone_bytes=len(standalone),
            shared_transport_bytes=shared.container_bytes,
            shared_amortized_bytes=shared.amortized_bytes,
            chosen_effective_bytes=float(len(standalone)),
            reuse_count=reuse_count,
            note="Standalone remains cheaper after charging shared-model cost.",
        )
