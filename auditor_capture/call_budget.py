from __future__ import annotations

from collections import Counter
from typing import Any


def calls_for_treatment(treatment: dict[str, Any], include_appeals_judge: bool = False) -> int:
    calls = 2
    if treatment["persuasion"] != "no_response":
        calls += 2
    if include_appeals_judge:
        calls += 1
    return calls


def plan_budget(
    case_count: int,
    treatments: list[dict[str, Any]],
    *,
    include_appeals_judge: bool = False,
) -> dict[str, Any]:
    per_condition = {
        treatment["treatment_id"]: calls_for_treatment(treatment, include_appeals_judge)
        for treatment in treatments
    }
    total = case_count * sum(per_condition.values())
    persuasion_counts = Counter(treatment["persuasion"] for treatment in treatments)
    return {
        "case_count": case_count,
        "treatment_count": len(treatments),
        "include_appeals_judge": include_appeals_judge,
        "calls_per_case_across_treatments": sum(per_condition.values()),
        "total_calls": total,
        "per_condition_calls_per_case": per_condition,
        "persuasion_condition_counts": dict(persuasion_counts),
    }


def balanced_single_assignment_budget(
    case_count: int,
    treatments: list[dict[str, Any]],
    *,
    include_appeals_judge: bool = False,
) -> dict[str, Any]:
    counts = Counter()
    for i in range(case_count):
        treatment = treatments[i % len(treatments)]
        counts[treatment["treatment_id"]] += 1
    total = 0
    per_condition_total: dict[str, int] = {}
    for treatment in treatments:
        treatment_id = treatment["treatment_id"]
        condition_total = counts[treatment_id] * calls_for_treatment(
            treatment,
            include_appeals_judge,
        )
        per_condition_total[treatment_id] = condition_total
        total += condition_total
    return {
        "case_count": case_count,
        "treatment_count": len(treatments),
        "assignment": "balanced_single_treatment_per_case",
        "include_appeals_judge": include_appeals_judge,
        "total_calls": total,
        "per_condition_total_calls": per_condition_total,
    }

