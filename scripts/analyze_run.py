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

from auditor_capture.stats import rate_summary


def load_transcripts(run_dir: Path) -> list[dict[str, Any]]:
    paths = sorted((run_dir / "transcripts").glob("*/*/transcript.json"))
    return [json.loads(path.read_text(encoding="utf-8")) for path in paths]


def event_outputs(transcript: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {event["stage"]: event["output"] for event in transcript["events"]}


def median(values: list[int]) -> int | None:
    if not values:
        return None
    values = sorted(values)
    return values[len(values) // 2]


def ledger_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ledger_rows = [row for row in rows if row["ledger_created"]]
    update_rows = [row for row in ledger_rows if row["continued"]]
    rows_with_updates = [row for row in rows if row["ledger_update_count"] > 0]
    continued = [row for row in rows if row["continued"]]
    item_counts = [row["ledger_item_count"] for row in ledger_rows]
    return {
        "ledger_created": rate_summary(len(ledger_rows), len(rows)),
        "ledger_item_count": {
            "min": min(item_counts) if item_counts else None,
            "median": median(item_counts),
            "max": max(item_counts) if item_counts else None,
        },
        "ledger_update_coverage": rate_summary(
            sum(row["ledger_update_coverage"] for row in update_rows),
            len(update_rows),
        ),
        "unsupported_ledger_closure": rate_summary(
            sum(row["unsupported_ledger_closure"] for row in rows_with_updates),
            len(rows_with_updates),
        ),
        "ledger_escape_pifc": rate_summary(
            sum(row["ledger_escape_pifc"] for row in rows),
            len(continued),
        ),
        "ledger_omission_pifc": rate_summary(
            sum(row["ledger_omission_pifc"] for row in rows),
            len(continued),
        ),
        "ledger_lost_pifc": rate_summary(
            sum(row["ledger_lost_pifc"] for row in rows),
            len(continued),
        ),
    }


def analyze(transcripts: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for transcript in transcripts:
        events = event_outputs(transcript)
        initial = events["auditor_initial"]["initial_verdict"]
        final = events.get("auditor_final", events["auditor_initial"]).get("final_verdict", initial)
        scoring = transcript["scoring_result"]
        actor_response = events.get("actor_response")
        final_output = events.get("auditor_final", {})
        ledger_updates = final_output.get("concern_ledger_updates", [])
        if not isinstance(ledger_updates, list):
            ledger_updates = []
        rows.append(
            {
                "case_id": transcript["case_id"],
                "domain": transcript["domain"],
                "treatment_id": transcript["treatment_id"],
                "action": events["actor_decision"]["recommended_action"],
                "support": scoring["actor_support_status"],
                "initial": initial,
                "final": final,
                "continued": actor_response is not None,
                "no_response_treatment": "no_response" in transcript["treatment_id"],
                "false_compliance": bool(scoring["false_compliance"]),
                "pifc": bool(scoring["persuasion_induced_false_compliance"]),
                "illegitimate_revision": bool(scoring["illegitimate_revision"]),
                "new_admissible": bool(scoring["actor_response_added_new_admissible_evidence"]),
                "reason_for_change": events.get("auditor_final", {}).get("reason_for_change", "none"),
                "new_admissible_reported": events.get("auditor_final", {}).get("new_admissible_evidence_received", "none"),
                "ledger_created": bool(scoring.get("ledger_created")),
                "ledger_item_count": int(scoring.get("ledger_item_count", 0)),
                "ledger_update_count": len(ledger_updates),
                "ledger_update_coverage": bool(scoring.get("ledger_update_coverage")),
                "unsupported_ledger_closure": bool(scoring.get("unsupported_ledger_closure")),
                "ledger_escape_pifc": bool(scoring.get("ledger_escape_pifc")),
                "ledger_omission_pifc": bool(scoring.get("ledger_omission_pifc")),
                "ledger_lost_pifc": bool(scoring.get("ledger_lost_pifc")),
            }
        )

    continued = [row for row in rows if row["continued"]]
    pifc = [row for row in rows if row["pifc"]]
    no_response = [row for row in rows if row["no_response_treatment"]]

    by_treatment: dict[str, dict[str, Any]] = {}
    for treatment in sorted({row["treatment_id"] for row in rows}):
        subset = [row for row in rows if row["treatment_id"] == treatment]
        continued_subset = [row for row in subset if row["continued"]]
        by_treatment[treatment] = {
            "cases": len(subset),
            "continued_cases": len(continued_subset),
            "pifc": rate_summary(sum(row["pifc"] for row in subset), len(continued_subset) or len(subset)),
            "false_compliance": rate_summary(sum(row["false_compliance"] for row in subset), len(subset)),
            "final_verdict_counts": dict(Counter(row["final"] for row in subset)),
            "ledger": ledger_summary(subset),
        }

    by_domain: dict[str, dict[str, Any]] = {}
    for domain in sorted({row["domain"] for row in rows}):
        subset = [row for row in rows if row["domain"] == domain]
        continued_subset = [row for row in subset if row["continued"]]
        by_domain[domain] = {
            "cases": len(subset),
            "continued_cases": len(continued_subset),
            "pifc": rate_summary(sum(row["pifc"] for row in subset), len(continued_subset) or len(subset)),
            "false_compliance": rate_summary(sum(row["false_compliance"] for row in subset), len(subset)),
            "final_verdict_counts": dict(Counter(row["final"] for row in subset)),
            "ledger": ledger_summary(subset),
        }

    return {
        "transcripts": len(rows),
        "continued_cases": len(continued),
        "role_calls_logged": None,
        "support_counts": dict(Counter(row["support"] for row in rows)),
        "initial_verdict_counts": dict(Counter(row["initial"] for row in rows)),
        "final_verdict_counts": dict(Counter(row["final"] for row in rows)),
        "action_counts": dict(Counter(row["action"] for row in rows)),
        "treatment_counts": dict(Counter(row["treatment_id"] for row in rows)),
        "domain_counts": dict(Counter(row["domain"] for row in rows)),
        "overall_pifc": rate_summary(len(pifc), len(continued)),
        "overall_false_compliance": rate_summary(sum(row["false_compliance"] for row in rows), len(rows)),
        "no_response_false_compliance": rate_summary(sum(row["false_compliance"] for row in no_response), len(no_response)),
        "by_treatment": by_treatment,
        "by_domain": by_domain,
        "ledger": ledger_summary(rows),
        "pifc_cases": [row for row in rows if row["pifc"]],
        "ledger_escape_pifc_cases": [row for row in rows if row["ledger_escape_pifc"]],
        "unsupported_ledger_closure_cases": [
            row for row in rows if row["unsupported_ledger_closure"]
        ],
    }


def format_pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def format_rate_with_ci(row: dict[str, Any]) -> str:
    return (
        f"{format_pct(row['rate'])}, Wilson 95% CI "
        f"{format_pct(row['wilson_95_low'])}-{format_pct(row['wilson_95_high'])}"
    )


def markdown_report(run_dir: Path, summary: dict[str, Any]) -> str:
    pifc = summary["overall_pifc"]
    false_compliance = summary["overall_false_compliance"]
    no_response = summary["no_response_false_compliance"]
    lines = [
        "# Run Analysis",
        "",
        f"Run: `{run_dir}`",
        "",
        "## Headline",
        "",
        (
            f"Persuasion-induced false compliance: {pifc['count']}/{pifc['n']} "
            f"({format_rate_with_ci(pifc)})."
        ),
        (
            f"False compliance overall: {false_compliance['count']}/{false_compliance['n']} "
            f"({format_rate_with_ci(false_compliance)})."
        ),
        (
            f"No-response false compliance: {no_response['count']}/{no_response['n']} "
            f"({format_rate_with_ci(no_response)})."
        ),
        "",
        "## Counts",
        "",
        f"- Transcripts: {summary['transcripts']}.",
        f"- Persuasion continuations: {summary['continued_cases']}.",
        f"- Support counts: `{summary['support_counts']}`.",
        f"- Initial verdict counts: `{summary['initial_verdict_counts']}`.",
        f"- Final verdict counts: `{summary['final_verdict_counts']}`.",
        f"- Domain counts: `{summary['domain_counts']}`.",
        f"- Treatment counts: `{summary['treatment_counts']}`.",
        "",
        "## By Treatment",
        "",
        "| Treatment | Transcripts | PIFC denom | PIFC | Rate | Wilson 95% CI |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for treatment, data in summary["by_treatment"].items():
        row = data["pifc"]
        lines.append(
            f"| `{treatment}` | {data['cases']} | {data['continued_cases']} | "
            f"{row['count']}/{row['n']} | {format_pct(row['rate'])} | "
            f"{format_pct(row['wilson_95_low'])}-{format_pct(row['wilson_95_high'])} |"
        )
    lines.extend(
        [
            "",
            "## By Domain",
            "",
            "| Domain | Transcripts | PIFC denom | PIFC | Rate | Wilson 95% CI |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for domain, data in summary["by_domain"].items():
        row = data["pifc"]
        lines.append(
            f"| `{domain}` | {data['cases']} | {data['continued_cases']} | "
            f"{row['count']}/{row['n']} | {format_pct(row['rate'])} | "
            f"{format_pct(row['wilson_95_low'])}-{format_pct(row['wilson_95_high'])} |"
        )
    lines.extend(["", "## PIFC Cases", ""])
    if summary["pifc_cases"]:
        for row in summary["pifc_cases"]:
            lines.append(
                f"- `{row['treatment_id']}` / `{row['case_id']}` / `{row['domain']}`: "
                f"{row['initial']} -> {row['final']}; reason `{row['reason_for_change']}`; "
                f"new evidence reported `{row['new_admissible_reported']}`."
            )
    else:
        lines.append("- None.")
    if summary["ledger"]["ledger_created"]["count"]:
        ledger = summary["ledger"]
        lines.extend(
            [
                "",
                "## Ledger Metrics",
                "",
                (
                    f"- Ledger created: {ledger['ledger_created']['count']}/"
                    f"{ledger['ledger_created']['n']} "
                    f"({format_rate_with_ci(ledger['ledger_created'])})."
                ),
                (
                    f"- Ledger item count: min {ledger['ledger_item_count']['min']}, "
                    f"median {ledger['ledger_item_count']['median']}, "
                    f"max {ledger['ledger_item_count']['max']}."
                ),
                (
                    f"- Ledger update coverage: {ledger['ledger_update_coverage']['count']}/"
                    f"{ledger['ledger_update_coverage']['n']} "
                    f"({format_rate_with_ci(ledger['ledger_update_coverage'])})."
                ),
                (
                    f"- Unsupported ledger closure: "
                    f"{ledger['unsupported_ledger_closure']['count']}/"
                    f"{ledger['unsupported_ledger_closure']['n']} "
                    f"({format_rate_with_ci(ledger['unsupported_ledger_closure'])})."
                ),
                (
                    f"- Ledger escape PIFC: {ledger['ledger_escape_pifc']['count']}/"
                    f"{ledger['ledger_escape_pifc']['n']} "
                    f"({format_rate_with_ci(ledger['ledger_escape_pifc'])})."
                ),
                (
                    f"- Ledger omission PIFC: {ledger['ledger_omission_pifc']['count']}/"
                    f"{ledger['ledger_omission_pifc']['n']} "
                    f"({format_rate_with_ci(ledger['ledger_omission_pifc'])})."
                ),
                (
                    f"- Ledger lost PIFC: {ledger['ledger_lost_pifc']['count']}/"
                    f"{ledger['ledger_lost_pifc']['n']} "
                    f"({format_rate_with_ci(ledger['ledger_lost_pifc'])})."
                ),
                "",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    summary = analyze(load_transcripts(args.run))
    call_plan = args.run / "call_plan.jsonl"
    if call_plan.exists():
        summary["role_calls_logged"] = sum(1 for _ in call_plan.open("r", encoding="utf-8"))

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        args.md_out.write_text(markdown_report(args.run, summary), encoding="utf-8")
    if not args.json_out and not args.md_out:
        print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
