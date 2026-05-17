#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auditor_capture.case_generation import load_jsonl
from auditor_capture.orchestrator import run_experiment


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--treatments", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--limit-cases", type=int)
    parser.add_argument("--condition", action="append", dest="conditions")
    parser.add_argument("--actor-model")
    parser.add_argument("--auditor-model")
    parser.add_argument("--assignment-seed", type=int)
    parser.add_argument("--include-appeals-judge", action="store_true")
    parser.add_argument(
        "--assignment",
        choices=["all_conditions", "balanced-stratified"],
        default="all_conditions",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    cases = load_jsonl(args.cases)
    if args.limit_cases is not None:
        cases = cases[: args.limit_cases]
    treatments = json.loads(args.treatments.read_text(encoding="utf-8"))
    if args.conditions:
        allowed = set(args.conditions)
        treatments = [t for t in treatments if t["treatment_id"] in allowed]
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if args.actor_model:
        manifest["actor_model"] = args.actor_model
    if args.auditor_model:
        manifest["auditor_model"] = args.auditor_model
    if args.include_appeals_judge:
        manifest["include_appeals_judge"] = True

    metrics = run_experiment(
        cases=cases,
        treatments=treatments,
        manifest=manifest,
        out_dir=args.out,
        dry_run=args.dry_run,
        execute=args.execute,
        assignment=args.assignment,
        assignment_seed=args.assignment_seed,
    )
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
