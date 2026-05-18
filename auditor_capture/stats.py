from __future__ import annotations

from math import sqrt
from typing import Any


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total < 0:
        raise ValueError("total must be non-negative")
    if successes < 0:
        raise ValueError("successes must be non-negative")
    if successes > total:
        raise ValueError("successes cannot exceed total")
    if total == 0:
        return (0.0, 0.0)

    p = successes / total
    denom = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denom
    margin = z * sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def rate_summary(successes: int, total: int) -> dict[str, Any]:
    low, high = wilson_interval(successes, total)
    return {
        "count": successes,
        "n": total,
        "rate": successes / total if total else 0.0,
        "wilson_95_low": low,
        "wilson_95_high": high,
    }


def add_rate_fields(target: dict[str, Any], key: str, successes: int, total: int) -> None:
    rate = rate_summary(successes, total)
    target[key] = successes
    target[f"{key}_rate_denominator"] = total
    target[f"{key}_rate"] = rate["rate"]
    target[f"{key}_rate_wilson_95_low"] = rate["wilson_95_low"]
    target[f"{key}_rate_wilson_95_high"] = rate["wilson_95_high"]
