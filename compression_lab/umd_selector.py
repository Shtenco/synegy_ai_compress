"""Unified MDL selector with Gabriel surface-aware routing.

The selector minimizes the complete operational description length:
L(model) + L(data|model) + encode/decode latency + access surface + switching.
"""
from dataclasses import dataclass
from functools import partial


@dataclass(frozen=True)
class Candidate:
    name: str
    size: int
    encode_ms: float
    model_cost: int = 0
    decode_ms: float = 0.0
    active_shells: int = 0
    random_access_cost: float = 0.0
    dependency_depth: int = 0
    switch_cost: float = 0.0


def score(
    c: Candidate,
    latency_weight: float = 0.1,
    *,
    decode_weight: float | None = None,
    surface_weight: float = 0.0,
    access_weight: float = 0.0,
    switch_weight: float = 0.0,
) -> float:
    """Return a byte-equivalent operational MDL score.

    Defaults preserve the original selector behavior. Gabriel-aware callers can
    price the decoding surface without confusing parameter count with runtime
    access cost.
    """
    if decode_weight is None:
        decode_weight = latency_weight
    return (
        c.size
        + c.model_cost
        + latency_weight * c.encode_ms
        + decode_weight * c.decode_ms
        + surface_weight * (c.active_shells + c.dependency_depth)
        + access_weight * c.random_access_cost
        + switch_weight * c.switch_cost
    )


def choose(candidates: list[Candidate], **weights: float) -> Candidate:
    if not candidates:
        raise ValueError("no candidates")
    return min(candidates, key=partial(score, **weights))
