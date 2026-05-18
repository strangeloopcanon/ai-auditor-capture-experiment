#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auditor_capture.call_budget import balanced_single_assignment_budget, plan_budget
from auditor_capture.case_generation import load_jsonl
from auditor_capture.orchestrator import run_experiment


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_repo_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def repo_display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def repeat_seed(seed_base: int, repeat_index: int) -> int:
    return seed_base + repeat_index - 1


def budget_for_assignment(
    *,
    case_count: int,
    treatments: list[dict[str, Any]],
    assignment: str,
    include_appeals_judge: bool,
) -> dict[str, Any]:
    if assignment == "all_conditions":
        return plan_budget(
            case_count,
            treatments,
            include_appeals_judge=include_appeals_judge,
        )
    if assignment == "balanced-stratified":
        return balanced_single_assignment_budget(
            case_count,
            treatments,
            include_appeals_judge=include_appeals_judge,
        )
    raise ValueError(f"Unknown assignment mode: {assignment}")


def expected_transcripts(case_count: int, treatment_count: int, assignment: str) -> int:
    if assignment == "all_conditions":
        return case_count * treatment_count
    if assignment == "balanced-stratified":
        return case_count
    raise ValueError(f"Unknown assignment mode: {assignment}")


def build_plan(config_path: Path, config: dict[str, Any], repeats: int, out_root: Path) -> dict[str, Any]:
    cases = load_jsonl(resolve_repo_path(config["cases"]))
    treatments = load_json(resolve_repo_path(config["treatments"]))
    manifest = load_json(resolve_repo_path(config["manifest"]))
    include_judge = bool(config.get("include_appeals_judge", manifest.get("include_appeals_judge", False)))
    assignment = config.get("assignment", "all_conditions")
    per_repeat_budget = budget_for_assignment(
        case_count=len(cases),
        treatments=treatments,
        assignment=assignment,
        include_appeals_judge=include_judge,
    )
    per_repeat_transcripts = expected_transcripts(len(cases), len(treatments), assignment)
    planned_counts = config.get("planned_repeat_counts", [3, 5, 10])
    seed_base = int(config["seed_base"])
    repeat_runs = [
        {
            "repeat_index": i,
            "seed": repeat_seed(seed_base, i),
            "out_dir": repo_display_path(out_root / f"repeat_{i:03d}_seed_{repeat_seed(seed_base, i)}"),
        }
        for i in range(1, repeats + 1)
    ]
    return {
        "replication_id": config["replication_id"],
        "config_path": repo_display_path(config_path),
        "cases": config["cases"],
        "treatments": config["treatments"],
        "manifest": config["manifest"],
        "assignment": assignment,
        "case_count": len(cases),
        "treatment_count": len(treatments),
        "expected_transcripts_per_repeat": per_repeat_transcripts,
        "max_calls_per_repeat": per_repeat_budget["total_calls"],
        "per_repeat_budget": per_repeat_budget,
        "repeat_count": repeats,
        "total_expected_transcripts": per_repeat_transcripts * repeats,
        "total_max_calls": per_repeat_budget["total_calls"] * repeats,
        "standard_repeat_budgets": {
            str(count): {
                "repeats": count,
                "expected_transcripts": per_repeat_transcripts * count,
                "max_calls": per_repeat_budget["total_calls"] * count,
            }
            for count in planned_counts
        },
        "seed_base": seed_base,
        "repeat_runs": repeat_runs,
    }


def analyze_run(run_dir: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "analyze_run.py"),
            "--run",
            str(run_dir),
            "--json-out",
            str(run_dir / "analysis.json"),
        ],
        check=True,
    )


def load_completed_run_summary(run_dir: Path) -> dict[str, Any]:
    metrics = load_json(run_dir / "metrics.json")
    analysis_path = run_dir / "analysis.json"
    analysis = load_json(analysis_path) if analysis_path.exists() else None
    call_plan = run_dir / "call_plan.jsonl"
    calls_logged = sum(1 for _ in call_plan.open("r", encoding="utf-8")) if call_plan.exists() else 0
    return {
        "run_dir": repo_display_path(run_dir),
        "transcripts": metrics["transcript_count"],
        "calls_logged": calls_logged,
        "persuasion_induced_false_compliance": metrics["persuasion_induced_false_compliance"],
        "persuasion_induced_false_compliance_rate": metrics[
            "persuasion_induced_false_compliance_rate"
        ],
        "persuasion_induced_false_compliance_rate_wilson_95_low": metrics.get(
            "persuasion_induced_false_compliance_rate_wilson_95_low"
        ),
        "persuasion_induced_false_compliance_rate_wilson_95_high": metrics.get(
            "persuasion_induced_false_compliance_rate_wilson_95_high"
        ),
        "false_compliance": metrics["false_compliance"],
        "false_compliance_rate": metrics["false_compliance_rate"],
        "false_compliance_rate_wilson_95_low": metrics.get(
            "false_compliance_rate_wilson_95_low"
        ),
        "false_compliance_rate_wilson_95_high": metrics.get(
            "false_compliance_rate_wilson_95_high"
        ),
        "analysis_path": repo_display_path(analysis_path),
        "analysis_summary": {
            "overall_pifc": analysis["overall_pifc"] if analysis else None,
            "overall_false_compliance": analysis["overall_false_compliance"] if analysis else None,
            "no_response_false_compliance": analysis["no_response_false_compliance"] if analysis else None,
            "pifc_case_count": len(analysis["pifc_cases"]) if analysis else None,
        },
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--repeats", required=True, type=int)
    parser.add_argument("--out-root", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan-only", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    if args.repeats < 1:
        raise ValueError("--repeats must be positive.")

    config = load_json(args.config)
    out_root = args.out_root or resolve_repo_path(config["out_root"])
    plan = build_plan(args.config, config, args.repeats, out_root)

    if args.plan_only:
        print(json.dumps(plan, indent=2, sort_keys=True))
        return

    write_json(out_root / "replication_plan.json", plan)
    cases = load_jsonl(resolve_repo_path(config["cases"]))
    treatments = load_json(resolve_repo_path(config["treatments"]))
    manifest = load_json(resolve_repo_path(config["manifest"]))
    if "actor_model" in config:
        manifest["actor_model"] = config["actor_model"]
    if "auditor_model" in config:
        manifest["auditor_model"] = config["auditor_model"]
    if "include_appeals_judge" in config:
        manifest["include_appeals_judge"] = bool(config["include_appeals_judge"])

    completed_runs = []
    for run in plan["repeat_runs"]:
        run_dir = resolve_repo_path(run["out_dir"])
        run_manifest = copy.deepcopy(manifest)
        run_manifest["replication_id"] = plan["replication_id"]
        run_manifest["replication_repeat_index"] = run["repeat_index"]
        run_manifest["assignment_seed"] = run["seed"]
        write_json(
            run_dir / "run_metadata.json",
            {
                "replication_id": plan["replication_id"],
                "repeat_index": run["repeat_index"],
                "repeat_count": args.repeats,
                "assignment": plan["assignment"],
                "assignment_seed": run["seed"],
                "cases": config["cases"],
                "treatments": config["treatments"],
                "manifest": config["manifest"],
                "max_calls": plan["max_calls_per_repeat"],
                "expected_transcripts": plan["expected_transcripts_per_repeat"],
                "mode": "execute" if args.execute else "dry_run",
            },
        )
        run_experiment(
            cases=cases,
            treatments=treatments,
            manifest=run_manifest,
            out_dir=run_dir,
            dry_run=args.dry_run,
            execute=args.execute,
            assignment=plan["assignment"],
            assignment_seed=run["seed"],
        )
        analyze_run(run_dir)
        completed_runs.append(load_completed_run_summary(run_dir))

    summary = {
        "replication_id": plan["replication_id"],
        "repeat_count": args.repeats,
        "mode": "execute" if args.execute else "dry_run",
        "planned_max_calls": plan["total_max_calls"],
        "planned_transcripts": plan["total_expected_transcripts"],
        "runs": completed_runs,
    }
    write_json(out_root / "replication_summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
