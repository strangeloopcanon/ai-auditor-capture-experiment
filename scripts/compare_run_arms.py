#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auditor_capture.stats import rate_summary


METRICS = (
    "persuasion_induced_false_compliance",
    "false_compliance",
    "ledger_escape_pifc",
    "ledger_omission_pifc",
    "ledger_lost_pifc",
    "unsupported_ledger_closure",
)


def load_transcript(run_dir: Path, treatment_id: str, case_id: str) -> dict[str, Any]:
    path = run_dir / "transcripts" / treatment_id / case_id / "transcript.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_treatment_transcripts(run_dir: Path, treatment_id: str) -> dict[str, dict[str, Any]]:
    treatment_dir = run_dir / "transcripts" / treatment_id
    if not treatment_dir.exists():
        raise FileNotFoundError(f"missing treatment transcript dir: {treatment_dir}")
    transcripts = {}
    for path in sorted(treatment_dir.glob("*/transcript.json")):
        transcript = json.loads(path.read_text(encoding="utf-8"))
        transcripts[transcript["case_id"]] = transcript
    if not transcripts:
        raise ValueError(f"no transcripts found under {treatment_dir}")
    return transcripts


def event_outputs(transcript: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {event["stage"]: event["output"] for event in transcript["events"]}


def continued(transcript: dict[str, Any]) -> bool:
    return any(event["stage"] == "actor_response" for event in transcript["events"])


def metric_denominator(metric: str, transcripts: list[dict[str, Any]]) -> int:
    if metric in {
        "persuasion_induced_false_compliance",
        "ledger_escape_pifc",
        "ledger_omission_pifc",
        "ledger_lost_pifc",
    }:
        return sum(1 for transcript in transcripts if continued(transcript))
    return len(transcripts)


def arm_summary(transcripts_by_case: dict[str, dict[str, Any]]) -> dict[str, Any]:
    transcripts = list(transcripts_by_case.values())
    out: dict[str, Any] = {
        "cases": len(transcripts),
        "continued_cases": sum(1 for transcript in transcripts if continued(transcript)),
    }
    for metric in METRICS:
        count = sum(1 for transcript in transcripts if transcript["scoring_result"].get(metric))
        out[metric] = rate_summary(count, metric_denominator(metric, transcripts))
    return out


def binom_cdf(k: int, n: int) -> float:
    return sum(math.comb(n, i) for i in range(k + 1)) / (2**n)


def mcnemar_exact(left_only: int, right_only: int) -> float:
    discordant = left_only + right_only
    if discordant == 0:
        return 1.0
    smaller = min(left_only, right_only)
    return min(1.0, 2 * binom_cdf(smaller, discordant))


def approx_rate_diff(left: dict[str, Any], right: dict[str, Any]) -> dict[str, float]:
    left_rate = left["rate"]
    right_rate = right["rate"]
    left_n = left["n"]
    right_n = right["n"]
    diff = left_rate - right_rate
    se = math.sqrt(
        (left_rate * (1 - left_rate) / left_n if left_n else 0)
        + (right_rate * (1 - right_rate) / right_n if right_n else 0)
    )
    if se == 0:
        low = high = diff
        p_value = 1.0
    else:
        z = diff / se
        low = diff - 1.96 * se
        high = diff + 1.96 * se
        p_value = math.erfc(abs(z) / math.sqrt(2))
    return {
        "left_minus_right_rate": diff,
        "approx_95_low": low,
        "approx_95_high": high,
        "approx_two_sided_p": p_value,
    }


def paired_metric(
    *,
    metric: str,
    case_ids: list[str],
    left_transcripts: dict[str, dict[str, Any]],
    right_transcripts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    left_only = []
    right_only = []
    both = []
    neither = []
    for case_id in case_ids:
        left_value = bool(left_transcripts[case_id]["scoring_result"].get(metric))
        right_value = bool(right_transcripts[case_id]["scoring_result"].get(metric))
        if left_value and right_value:
            both.append(case_id)
        elif left_value:
            left_only.append(case_id)
        elif right_value:
            right_only.append(case_id)
        else:
            neither.append(case_id)
    return {
        "left_only": len(left_only),
        "right_only": len(right_only),
        "both": len(both),
        "neither": len(neither),
        "left_only_case_ids": left_only,
        "right_only_case_ids": right_only,
        "both_case_ids": both,
        "mcnemar_exact_p": mcnemar_exact(len(left_only), len(right_only)),
    }


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def rate_text(rate: dict[str, Any]) -> str:
    return (
        f"{rate['count']}/{rate['n']} = {pct(rate['rate'])} "
        f"(95% CI {pct(rate['wilson_95_low'])}-{pct(rate['wilson_95_high'])})"
    )


def markdown(result: dict[str, Any]) -> str:
    left = result["arms"]["left"]
    right = result["arms"]["right"]
    lines = [
        f"# {result['comparison_id']}",
        "",
        result["question"],
        "",
        "## Arm Results",
        "",
        "| Arm | Treatment | Cases | Continued | PIFC | Overall false compliance |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
        (
            f"| {left['label']} | `{left['treatment_id']}` | {left['summary']['cases']} | "
            f"{left['summary']['continued_cases']} | "
            f"{rate_text(left['summary']['persuasion_induced_false_compliance'])} | "
            f"{rate_text(left['summary']['false_compliance'])} |"
        ),
        (
            f"| {right['label']} | `{right['treatment_id']}` | {right['summary']['cases']} | "
            f"{right['summary']['continued_cases']} | "
            f"{rate_text(right['summary']['persuasion_induced_false_compliance'])} | "
            f"{rate_text(right['summary']['false_compliance'])} |"
        ),
        "",
        "## Paired Comparison",
        "",
        "| Metric | Left only | Right only | Both | Neither | Exact McNemar p | Left minus right |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for metric, paired in result["paired_discordance"].items():
        diff = result["left_minus_right"][metric]
        lines.append(
            f"| {metric} | {paired['left_only']} | {paired['right_only']} | "
            f"{paired['both']} | {paired['neither']} | {paired['mcnemar_exact_p']:.6g} | "
            f"{pct(diff['left_minus_right_rate'])} "
            f"(95% approx {pct(diff['approx_95_low'])}-{pct(diff['approx_95_high'])}) |"
        )
    lines.append("")
    return "\n".join(lines)


def compare(args: argparse.Namespace) -> dict[str, Any]:
    left_transcripts = load_treatment_transcripts(args.left_run, args.left_treatment)
    right_transcripts = load_treatment_transcripts(args.right_run, args.right_treatment)
    left_case_ids = set(left_transcripts)
    right_case_ids = set(right_transcripts)
    if left_case_ids != right_case_ids:
        missing_left = sorted(right_case_ids - left_case_ids)
        missing_right = sorted(left_case_ids - right_case_ids)
        raise ValueError(
            "case sets differ: "
            f"missing from left={missing_left[:5]}, missing from right={missing_right[:5]}"
        )
    case_ids = sorted(left_case_ids)
    left_summary = arm_summary(left_transcripts)
    right_summary = arm_summary(right_transcripts)
    paired = {
        metric: paired_metric(
            metric=metric,
            case_ids=case_ids,
            left_transcripts=left_transcripts,
            right_transcripts=right_transcripts,
        )
        for metric in METRICS
    }
    diffs = {
        metric: approx_rate_diff(left_summary[metric], right_summary[metric])
        for metric in METRICS
    }
    return {
        "comparison_id": args.comparison_id,
        "question": args.question,
        "case_count": len(case_ids),
        "arms": {
            "left": {
                "label": args.left_label,
                "run": str(args.left_run),
                "treatment_id": args.left_treatment,
                "summary": left_summary,
            },
            "right": {
                "label": args.right_label,
                "run": str(args.right_run),
                "treatment_id": args.right_treatment,
                "summary": right_summary,
            },
        },
        "paired_discordance": paired,
        "left_minus_right": diffs,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison-id", required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--left-label", required=True)
    parser.add_argument("--left-run", required=True, type=Path)
    parser.add_argument("--left-treatment", required=True)
    parser.add_argument("--right-label", required=True)
    parser.add_argument("--right-run", required=True, type=Path)
    parser.add_argument("--right-treatment", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    result = compare(args)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "comparison.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.out / "comparison.md").write_text(markdown(result), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
