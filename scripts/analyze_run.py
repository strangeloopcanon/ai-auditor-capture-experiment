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


def analyze(transcripts: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for transcript in transcripts:
        events = event_outputs(transcript)
        initial = events["auditor_initial"]["initial_verdict"]
        final = events.get("auditor_final", events["auditor_initial"]).get("final_verdict", initial)
        scoring = transcript["scoring_result"]
        actor_response = events.get("actor_response")
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
        "pifc_cases": [row for row in rows if row["pifc"]],
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
        "| Treatment | Cases | Continued | PIFC | Rate | Wilson 95% CI |",
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
            "| Domain | Cases | Continued | PIFC | Rate | Wilson 95% CI |",
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
