#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auditor_capture.call_budget import balanced_single_assignment_budget, plan_budget
from auditor_capture.case_generation import load_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--treatments", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--include-appeals-judge", action="store_true")
    args = parser.parse_args()

    cases = load_jsonl(args.cases)
    treatments = json.loads(args.treatments.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    include_judge = args.include_appeals_judge or bool(manifest.get("include_appeals_judge"))
    all_conditions = plan_budget(len(cases), treatments, include_appeals_judge=include_judge)
    single_assignment = balanced_single_assignment_budget(
        len(cases),
        treatments,
        include_appeals_judge=include_judge,
    )
    print(json.dumps({"all_conditions": all_conditions, "balanced_single_assignment": single_assignment}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
