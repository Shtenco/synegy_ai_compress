from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
import struct
import zlib
import brotli

try:
    from .omnia_rex_v1 import (
        OmniaREXV1,
        R_RAW, R_BROTLI, R_BWT, R_SP_SPARSE, R_SP_BROTLI,
        _pack, _with_params, _sp_params, _spatial_residual, _sparse_encode,
        _widths, bwt,
    )
except ImportError:
    from omnia_rex_v1 import (
        OmniaREXV1,
        R_RAW, R_BROTLI, R_BWT, R_SP_SPARSE, R_SP_BROTLI,
        _pack, _with_params, _sp_params, _spatial_residual, _sparse_encode,
        _widths, bwt,
    )


@dataclass(frozen=True)
class V3Features:
    entropy: float
    zero: float
    repeat16: float
    delta_entropy: float
    lag256_equal: float


@dataclass(frozen=True)
class V3Decision:
    coarse_family: str
    exact_family: str
    max_prediction_rate: float | None


def _entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    return -sum((v / n) * math.log2(v / n) for v in counts.values())


def extract_v3_features(data: bytes) -> V3Features:
    data = bytes(data)
    n = max(1, len(data))
    delta = bytes(((data[i] - data[i - 1]) & 255) for i in range(1, len(data)))
    atoms = [data[i:i + 16] for i in range(0, max(0, len(data) - 15), 16)]
    return V3Features(
        entropy=_entropy(data),
        zero=data.count(0) / n,
        repeat16=1.0 - len(set(atoms)) / len(atoms) if atoms else 0.0,
        delta_entropy=_entropy(delta),
        lag256_equal=(
            sum(data[i] == data[i - 256] for i in range(256, len(data))) / n
            if len(data) > 256 else 0.0
        ),
    )


class HierarchicalRouterV3:
    """Frozen V3 hierarchy.

    Thresholds were frozen before the second external file-suite test.
    The router affects search cost only; exactness still comes from each
    candidate's reversible decoder plus the outer SHA-256 contract.
    """

    def coarse(self, f: V3Features) -> str:
        if f.zero > 0.90:
            return "bwt_mtf_rank"
        if f.entropy > 7.90:
            if f.repeat16 < 0.05 and f.lag256_equal < 0.05:
                return "raw"
            return "spatial"
        if f.delta_entropy < 2.0 or f.lag256_equal > 0.50:
            return "spatial"
        return "brotli11"

    def spatial_mode(self, source: bytes, f: V3Features) -> tuple[str, float]:
        # Highly periodic high-entropy streams can have almost zero first-order
        # residual entropy even when a different predictor has many exact hits.
        if f.entropy > 7.90 and f.delta_entropy < 0.50:
            return "spatial_residual", 0.0

        best_exact = 0.0
        for width in _widths(len(source)):
            for filt in (0, 1, 2):
                residual = _spatial_residual(source, width, filt)
                exact = residual.count(0) / max(1, len(residual))
                best_exact = max(best_exact, exact)

        # Theory-motivated sparse regime: <=10% exceptions.
        if best_exact >= 0.90:
            return "spatial_sparse", best_exact
        return "spatial_residual", best_exact

    def decide(self, source: bytes) -> V3Decision:
        f = extract_v3_features(source)
        coarse = self.coarse(f)
        if coarse == "spatial":
            exact, rate = self.spatial_mode(source, f)
            return V3Decision(coarse, exact, rate)
        return V3Decision(coarse, coarse, None)


class OmniaREXV3Fast:
    """Fast exact OMNIA-REX path.

    It evaluates one routed family plus a zero-cost-to-measure RAW fallback.
    Archives use the V1 wire format, so the V1 decoder remains authoritative.
    """

    name = "SHTENCO OMNIA-REX V3 FAST"
    family = "SHTENCO-OMNIA-REX"
    def __init__(self) -> None:
        self.router = HierarchicalRouterV3()
        self.decoder = OmniaREXV1(include_legacy=False)
        self.last_mode = "uninitialized"
        self.last_decision: V3Decision | None = None

    def _spatial_candidates(self, source: bytes, mode: str) -> list[bytes]:
        out: list[bytes] = []
        for width in _widths(len(source)):
            for filt in (0, 1, 2):
                residual = _spatial_residual(source, width, filt)
                params = _sp_params(width, filt)
                if mode == "spatial_residual":
                    out.append(_pack(
                        R_SP_BROTLI, source, _with_params(params, brotli.compress(residual, quality=11))
                    ))
                else:
                    sparse = _sparse_encode(residual)
                    z0 = zlib.compress(sparse, 9)
                    out.append(_pack(R_SP_SPARSE, source, _with_params(params, z0)))
        return out

    def compress(self, source: bytes) -> bytes:
        source = bytes(source)
        decision = self.router.decide(source)
        self.last_decision = decision
        raw = _pack(R_RAW, source, source)
        candidates = [raw]

        if decision.exact_family == "raw":
            pass
        elif decision.exact_family == "brotli11":
            candidates.append(_pack(R_BROTLI, source, brotli.compress(source, quality=11)))
        elif decision.exact_family == "bwt_mtf_rank":
            transformed, row = bwt.bwt(source)
            ranks = bwt.mtf_encode(transformed)
            candidates.append(_pack(
                R_BWT,
                source,
                _with_params(struct.pack(">I", row), brotli.compress(ranks, quality=11)),
            ))
        elif decision.exact_family in ("spatial_residual", "spatial_sparse"):
            candidates.extend(self._spatial_candidates(source, decision.exact_family))
        else:
            raise ValueError(f"unknown V3 family {decision.exact_family}")

        valid = []
        for archive in candidates:
            if self.decoder.decompress(archive) == source:
                valid.append(archive)
        if not valid:
            raise RuntimeError("no exact V3 FAST candidate")
        best = min(valid, key=len)
        self.last_mode = decision.exact_family if best is not raw else "raw"
        return best

    def decompress(self, archive: bytes) -> bytes:
        return self.decoder.decompress(archive)


class OmniaREXV3:
    """Two-mode V3 system.

    FAST: frozen hierarchy for low search cost.
    MAX: exhaustive V1/legacy portfolio for minimum bytes inside the portfolio.
    """

    name = "SHTENCO OMNIA-REX V3"
    family = "SHTENCO-OMNIA-REX"

    def __init__(self) -> None:
        self.fast = OmniaREXV3Fast()
        self.max = OmniaREXV1(include_legacy=True, include_math=True)

    def compress(self, source: bytes, *, mode: str = "fast") -> bytes:
        if mode == "fast":
            return self.fast.compress(source)
        if mode == "max":
            return self.max.compress(source)
        raise ValueError("mode must be fast or max")

    def decompress(self, archive: bytes) -> bytes:
        # Both modes retain V1-compatible exact container semantics.
        try:
            return self.fast.decompress(archive)
        except Exception:
            return self.max.decompress(archive)
