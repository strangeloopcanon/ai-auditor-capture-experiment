#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_transcript(run: str, treatment_id: str, case_id: str) -> dict[str, Any]:
    path = ROOT / run / "transcripts" / treatment_id / case_id / "transcript.json"
    return json.loads(path.read_text(encoding="utf-8"))


def events(transcript: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {event["stage"]: event["output"] for event in transcript["events"]}


def mechanism_for(archetype: str, final: dict[str, Any]) -> str:
    reason = final.get("reason_for_change")
    new_evidence = final.get("new_admissible_evidence_received")
    if new_evidence == "no" and reason in {"actor_explanation", "reinterpretation"}:
        if "draft_mitigation" in archetype:
            return "Draft mitigation was converted into a caveated certification path."
        if "eval_coverage_gap" in archetype:
            return "Missing named-context evaluation was converted into a disclosure caveat."
        if "materiality_dispute" in archetype:
            return "Open materiality question was converted into a caveated operational-readiness pass."
        if "rollout_monitoring" in archetype:
            return "Unclosed disclosure obligation was converted into a pre-launch condition."
        return "Unresolved concern was converted into a caveated pass without new evidence."
    return "Other final-verdict movement."


def short_list(values: list[str], *, limit: int = 2) -> str:
    if not values:
        return ""
    trimmed = values[:limit]
    suffix = "" if len(values) <= limit else f" (+{len(values) - limit} more)"
    return "; ".join(trimmed) + suffix


def build_review(comparison: dict[str, Any]) -> dict[str, Any]:
    left = comparison["arms"]["left"]
    right = comparison["arms"]["right"]
    left_run = left["run"]
    right_run = right["run"]
    left_treatment = left["treatment_id"]
    right_treatment = right["treatment_id"]
    pifc = comparison["paired_discordance"]["persuasion_induced_false_compliance"]
    groups = {
        "left_only": pifc["left_only_case_ids"],
        "right_only": pifc["right_only_case_ids"],
        "both": pifc["both_case_ids"],
    }
    rows = []
    for group, case_ids in groups.items():
        for case_id in case_ids:
            left_transcript = load_transcript(left_run, left_treatment, case_id)
            right_transcript = load_transcript(right_run, right_treatment, case_id)
            left_events = events(left_transcript)
            right_events = events(right_transcript)
            left_initial = left_events["auditor_initial"]
            left_final = left_events.get("auditor_final", {})
            right_initial = right_events["auditor_initial"]
            right_final = right_events.get("auditor_final", {})
            archetype = left_transcript["ground_truth_labels"]["archetype"]
            rows.append(
                {
                    "case_id": case_id,
                    "group": group,
                    "domain": left_transcript["domain"],
                    "archetype": archetype,
                    "mechanism": mechanism_for(archetype, left_final),
                    "left_initial": left_initial.get("initial_verdict"),
                    "left_final": left_final.get("final_verdict", left_initial.get("initial_verdict")),
                    "left_reason_for_change": left_final.get("reason_for_change", "none"),
                    "left_new_admissible_evidence_received": left_final.get(
                        "new_admissible_evidence_received", "no"
                    ),
                    "right_initial": right_initial.get("initial_verdict"),
                    "right_final": right_final.get("final_verdict", right_initial.get("initial_verdict")),
                    "right_reason_for_change": right_final.get("reason_for_change", "none"),
                    "left_initial_concerns": left_initial.get("specific_concerns", []),
                    "left_remaining_concerns": left_final.get("remaining_concerns", []),
                    "left_actor_argument_summary": left_events.get("actor_response", {}).get(
                        "argument_summary", ""
                    ),
                    "left_final_rationale": left_final.get("final_rationale", ""),
                }
            )
    left_only = [row for row in rows if row["group"] == "left_only"]
    return {
        "comparison_id": comparison["comparison_id"],
        "left_label": left["label"],
        "right_label": right["label"],
        "counts": {
            "left_only_pifc": len(left_only),
            "right_only_pifc": len([row for row in rows if row["group"] == "right_only"]),
            "both_pifc": len([row for row in rows if row["group"] == "both"]),
        },
        "left_only_by_archetype": dict(Counter(row["archetype"] for row in left_only)),
        "left_only_by_mechanism": dict(Counter(row["mechanism"] for row in left_only)),
        "left_only_reason_for_change": dict(Counter(row["left_reason_for_change"] for row in left_only)),
        "rows": rows,
    }


def md_table_count(counter: dict[str, int], key_name: str) -> list[str]:
    lines = [f"| {key_name} | Count |", "| --- | ---: |"]
    for key, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {key} | {count} |")
    return lines


def markdown(review: dict[str, Any]) -> str:
    lines = [
        f"# Mechanism Case Review: {review['comparison_id']}",
        "",
        (
            f"This review inspects PIFC cases from the paired `{review['left_label']}` versus "
            f"`{review['right_label']}` comparison."
        ),
        "",
        "## Summary",
        "",
        (
            f"- `{review['left_label']}` only: {review['counts']['left_only_pifc']} PIFC cases."
        ),
        (
            f"- `{review['right_label']}` only: {review['counts']['right_only_pifc']} PIFC cases."
        ),
        f"- Both arms: {review['counts']['both_pifc']} PIFC cases.",
        "",
        "The dominant pattern is not that new evidence closes the audit concern. The common movement is from an initial concern to `compliant_with_caveats` after the actor reframes the same record as a narrower, caveated certification path.",
        "",
        "## Left-Only PIFC by Archetype",
        "",
        *md_table_count(review["left_only_by_archetype"], "Archetype"),
        "",
        "## Left-Only PIFC by Mechanism",
        "",
        *md_table_count(review["left_only_by_mechanism"], "Mechanism"),
        "",
        "## Case-Level Review",
        "",
        "| Group | Case | Archetype | Left verdict | Right verdict | Left reason | Left new evidence | Mechanism | Initial concerns excerpt | Remaining concerns excerpt |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in review["rows"]:
        lines.append(
            f"| {row['group']} | `{row['case_id']}` | `{row['archetype']}` | "
            f"{row['left_initial']} -> {row['left_final']} | "
            f"{row['right_initial']} -> {row['right_final']} | "
            f"{row['left_reason_for_change']} | "
            f"{row['left_new_admissible_evidence_received']} | "
            f"{row['mechanism']} | "
            f"{short_list(row['left_initial_concerns'])} | "
            f"{short_list(row['left_remaining_concerns'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison", required=True, type=Path)
    parser.add_argument("--json-out", required=True, type=Path)
    parser.add_argument("--md-out", required=True, type=Path)
    args = parser.parse_args()

    comparison = json.loads(args.comparison.read_text(encoding="utf-8"))
    review = build_review(comparison)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(review, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.md_out.write_text(markdown(review), encoding="utf-8")
    print(json.dumps(review["counts"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
