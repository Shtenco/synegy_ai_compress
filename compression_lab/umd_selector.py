"""UMD selector prototype.

Chooses a codec plan by minimizing description length:
L(model)+L(data|model)+latency_penalty+switch_penalty.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    name: str
    size: int
    encode_ms: float
    model_cost: int = 0


def score(c: Candidate, latency_weight: float = 0.1) -> float:
    return c.size + c.model_cost + latency_weight * c.encode_ms


def choose(candidates: list[Candidate]) -> Candidate:
    if not candidates:
        raise ValueError("no candidates")
    return min(candidates, key=score)
