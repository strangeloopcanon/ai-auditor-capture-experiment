#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auditor_capture.case_generation import (
    generate_borderline_cases,
    generate_cases,
    generate_locked_stress_cases,
    write_jsonl,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cases-per-domain", type=int, default=50)
    parser.add_argument("--mode", choices=["standard", "locked-stress", "borderline"], default="standard")
    args = parser.parse_args()

    if args.mode == "locked-stress":
        cases = generate_locked_stress_cases(args.cases_per_domain)
    elif args.mode == "borderline":
        cases = generate_borderline_cases(args.cases_per_domain)
    else:
        cases = generate_cases(args.cases_per_domain)
    write_jsonl(cases, args.output)
    print(f"wrote {len(cases)} cases to {args.output}")


if __name__ == "__main__":
    main()
