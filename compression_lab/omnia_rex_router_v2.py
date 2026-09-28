from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
from typing import Any, Iterable

FAMILY_NAMES = (
    "brotli11",
    "bwt_mtf_rank",
    "lzma9",
    "ppm_anti_exp",
    "raw",
    "spatial_residual",
    "spatial_sparse",
    "zlib9",
)

FEATURE_NAMES = (
    "adjacent",
    "delta_entropy",
    "entropy",
    "lag16_equal",
    "lag256_equal",
    "n",
    "printable",
    "repeat16",
    "smooth",
    "unique_byte_ratio",
    "xor1_entropy",
    "zero",
)


def _entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    return -sum((v / n) * math.log2(v / n) for v in counts.values())


def extract_features(data: bytes) -> dict[str, float]:
    data = bytes(data)
    n = max(1, len(data))
    delta = bytes(((data[i] - data[i - 1]) & 255) for i in range(1, len(data)))
    xor1 = bytes((data[i] ^ data[i - 1]) for i in range(1, len(data)))
    atoms = [data[i:i + 16] for i in range(0, max(0, len(data) - 15), 16)]
    return {
        "n": float(len(data)),
        "entropy": _entropy(data),
        "printable": sum(b in (9, 10, 13) or 32 <= b < 127 for b in data) / n,
        "zero": data.count(0) / n,
        "adjacent": sum(data[i] == data[i - 1] for i in range(1, len(data))) / n,
        "smooth": sum(abs(data[i] - data[i - 1]) <= 2 for i in range(1, len(data))) / n,
        "repeat16": 1.0 - len(set(atoms)) / len(atoms) if atoms else 0.0,
        "unique_byte_ratio": len(set(data)) / 256.0,
        "delta_entropy": _entropy(delta),
        "xor1_entropy": _entropy(xor1),
        "lag16_equal": (
            sum(data[i] == data[i - 16] for i in range(16, len(data))) / n
            if len(data) > 16 else 0.0
        ),
        "lag256_equal": (
            sum(data[i] == data[i - 256] for i in range(256, len(data))) / n
            if len(data) > 256 else 0.0
        ),
    }


def feature_vector(features: dict[str, float]) -> list[float]:
    return [float(features[k]) for k in FEATURE_NAMES]


def candidate_family(name: str) -> str:
    low = name.lower()
    if low == "raw":
        return "raw"
    if low.startswith("zlib"):
        return "zlib9"
    if low.startswith("lzma"):
        return "lzma9"
    if low.startswith("brotli"):
        return "brotli11"
    if low.startswith("ppm-rex"):
        return "ppm_anti_exp"
    if low.startswith("bwt-mtf"):
        return "bwt_mtf_rank"
    if low.startswith("spatial-") and low.endswith("-sparse"):
        return "spatial_sparse"
    if low.startswith("spatial-"):
        return "spatial_residual"
    return "other"


def family_costs(engine: Any, source: bytes) -> dict[str, int]:
    """Measure V1 built-in candidates and collapse parameter variants by family."""
    costs: dict[str, int] = {}
    for c in engine._builtin_candidates(bytes(source)):  # intentional research API
        family = candidate_family(c.name)
        if family == "other":
            continue
        costs[family] = min(costs.get(family, 1 << 62), len(c.archive))
    return costs


@dataclass(frozen=True)
class RouterDecision:
    predicted_order: tuple[str, ...]
    selected_families: tuple[str, ...]
    guard_families: tuple[str, ...]


class ExtraTreesCostRouter:
    """Predict per-family description length, then evaluate only Top-K families."""

    def __init__(self, top_k: int = 2, random_state: int = 123) -> None:
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        self.top_k = top_k
        self.random_state = random_state
        self.model = None
        self.families: tuple[str, ...] = ()

    def fit(self, rows: Iterable[dict[str, Any]]) -> "ExtraTreesCostRouter":
        try:
            import numpy as np
            from sklearn.ensemble import ExtraTreesRegressor
        except Exception as exc:
            raise RuntimeError("router training requires numpy + scikit-learn") from exc
        rows = list(rows)
        families = sorted(set().union(*(row["costs"].keys() for row in rows)))
        x = np.asarray([feature_vector(row["features"]) for row in rows], dtype=float)
        y = np.asarray(
            [[math.log2(row["costs"][f]) for f in families] for row in rows],
            dtype=float,
        )
        model = ExtraTreesRegressor(
            n_estimators=400,
            min_samples_leaf=1,
            max_features=1.0,
            random_state=self.random_state,
            n_jobs=-1,
        )
        model.fit(x, y)
        self.model = model
        self.families = tuple(families)
        return self

    @staticmethod
    def guard_families(features: dict[str, float]) -> list[str]:
        """Frozen after development-corpus error analysis.

        These guards are deliberately simple and must be evaluated on later
        external corpora without retuning before being promoted.
        """
        out: list[str] = []
        if features["zero"] > 0.90:
            out.append("bwt_mtf_rank")
        if (
            features["entropy"] > 7.90
            and features["repeat16"] < 0.05
            and features["lag256_equal"] < 0.05
        ):
            out.append("raw")
        return out

    def decide(
        self,
        features: dict[str, float],
        *,
        available_families: Iterable[str] | None = None,
    ) -> RouterDecision:
        if self.model is None:
            raise RuntimeError("router is not fitted")
        import numpy as np
        available = set(available_families or self.families)
        pred = self.model.predict(np.asarray([feature_vector(features)], dtype=float))[0]
        order = [
            family
            for _, family in sorted(zip(pred, self.families))
            if family in available
        ]
        chosen = list(order[: self.top_k])
        guards = [
            f for f in self.guard_families(features)
            if f in available and f not in chosen
        ]
        chosen.extend(guards)
        return RouterDecision(tuple(order), tuple(chosen), tuple(guards))


def evaluate_decision(costs: dict[str, int], decision: RouterDecision) -> dict[str, Any]:
    oracle_family = min(costs, key=costs.get)
    oracle_bytes = costs[oracle_family]
    selected = [f for f in decision.selected_families if f in costs]
    if not selected:
        raise ValueError("router selected no available family")
    chosen_family = min(selected, key=lambda f: costs[f])
    chosen_bytes = costs[chosen_family]
    return {
        "oracle_family": oracle_family,
        "oracle_bytes": oracle_bytes,
        "chosen_family": chosen_family,
        "chosen_bytes": chosen_bytes,
        "regret_pct": 100.0 * (chosen_bytes / oracle_bytes - 1.0),
        "oracle_in_selected": oracle_family in selected,
        "families_evaluated": len(selected),
    }
