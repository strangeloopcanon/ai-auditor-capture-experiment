#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auditor_capture.orchestrator import aggregate_metrics, append_jsonl, repo_display_path, write_json


RAW_ACCESS_TREATMENTS = (
    "H3_raw_hidden_access_integrity",
    "H4_raw_known_access_integrity",
)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_filtered_jsonl(
    *,
    destination: Path,
    source_runs: list[Path],
    filename: str,
    treatment_ids: set[str],
) -> None:
    if destination.exists():
        destination.unlink()
    for run in source_runs:
        for row in _load_jsonl(run / filename):
            if row.get("treatment_id") in treatment_ids:
                append_jsonl(destination, row)


def _rewrite_call_plan_paths(call_plan_path: Path, out_dir: Path) -> None:
    rows = _load_jsonl(call_plan_path)
    if call_plan_path.exists():
        call_plan_path.unlink()
    for row in rows:
        output_path = (
            out_dir
            / "transcripts"
            / row["treatment_id"]
            / row["case_id"]
            / f"{row['stage']}.json"
        )
        row["output_path"] = repo_display_path(output_path)
        append_jsonl(call_plan_path, row)


def _copy_transcripts(
    *,
    source_runs: list[Path],
    out_dir: Path,
    treatment_ids: set[str],
) -> list[dict[str, Any]]:
    transcripts: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for run in source_runs:
        for treatment_id in sorted(treatment_ids):
            treatment_dir = run / "transcripts" / treatment_id
            if not treatment_dir.exists():
                continue
            for transcript_path in sorted(treatment_dir.glob("*/transcript.json")):
                transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
                key = (transcript["treatment_id"], transcript["case_id"])
                if key in seen:
                    raise ValueError(f"duplicate transcript in combined run: {key}")
                seen.add(key)
                target_case_dir = out_dir / "transcripts" / treatment_id / transcript["case_id"]
                target_case_dir.mkdir(parents=True, exist_ok=True)
                for event in transcript["events"]:
                    stage_output_path = target_case_dir / f"{event['stage']}.json"
                    write_json(stage_output_path, event["output"])
                    event["output_path"] = repo_display_path(stage_output_path)
                write_json(target_case_dir / "transcript.json", transcript)
                transcripts.append(transcript)
    return transcripts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-run", type=Path, required=True)
    parser.add_argument("--extension-run", type=Path, action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cases", required=True)
    parser.add_argument("--treatments", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--run-label", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    source_runs = [args.base_run] + args.extension_run
    missing_runs = [str(run) for run in source_runs if not run.exists()]
    if missing_runs:
        raise FileNotFoundError(f"missing source runs: {', '.join(missing_runs)}")

    if args.out.exists():
        if not args.force:
            raise FileExistsError(f"{args.out} already exists; pass --force to replace it")
        shutil.rmtree(args.out)
    args.out.mkdir(parents=True)

    treatment_ids = set(RAW_ACCESS_TREATMENTS)
    transcripts = _copy_transcripts(
        source_runs=source_runs,
        out_dir=args.out,
        treatment_ids=treatment_ids,
    )
    _write_filtered_jsonl(
        destination=args.out / "assignment.jsonl",
        source_runs=source_runs,
        filename="assignment.jsonl",
        treatment_ids=treatment_ids,
    )
    _write_filtered_jsonl(
        destination=args.out / "call_plan.jsonl",
        source_runs=source_runs,
        filename="call_plan.jsonl",
        treatment_ids=treatment_ids,
    )
    _rewrite_call_plan_paths(args.out / "call_plan.jsonl", args.out)
    _write_filtered_jsonl(
        destination=args.out / "case_scores.jsonl",
        source_runs=source_runs,
        filename="case_scores.jsonl",
        treatment_ids=treatment_ids,
    )
    write_json(args.out / "metrics.json", aggregate_metrics(transcripts))
    write_json(
        args.out / "run_metadata.json",
        {
            "run_label": args.run_label,
            "execution_mode": "incremental_reuse_existing_raw_access_lanes",
            "base_run": str(args.base_run),
            "extension_runs": [str(run) for run in args.extension_run],
            "combined_treatment_lanes": sorted(treatment_ids),
            "cases": args.cases,
            "treatments": args.treatments,
            "manifest": args.manifest,
            "transcript_count": len(transcripts),
        },
    )
    print(json.dumps({"transcript_count": len(transcripts)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
