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


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _copy_transcripts(source_runs: list[Path], out_dir: Path) -> list[dict[str, Any]]:
    transcripts: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for run in source_runs:
        for transcript_path in sorted((run / "transcripts").glob("*/*/transcript.json")):
            transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
            key = (transcript["treatment_id"], transcript["case_id"])
            if key in seen:
                raise ValueError(f"duplicate transcript in combined run: {key}")
            seen.add(key)

            target_case_dir = out_dir / "transcripts" / transcript["treatment_id"] / transcript["case_id"]
            target_case_dir.mkdir(parents=True, exist_ok=True)
            for event in transcript["events"]:
                stage_output_path = target_case_dir / f"{event['stage']}.json"
                write_json(stage_output_path, event["output"])
                event["output_path"] = repo_display_path(stage_output_path)
            write_json(target_case_dir / "transcript.json", transcript)
            transcripts.append(transcript)
    return transcripts


def _merge_jsonl(source_runs: list[Path], out_path: Path, filename: str) -> None:
    if out_path.exists():
        out_path.unlink()
    for run in source_runs:
        for row in _load_jsonl(run / filename):
            if filename == "call_plan.jsonl":
                output_path = (
                    out_path.parent
                    / "transcripts"
                    / row["treatment_id"]
                    / row["case_id"]
                    / f"{row['stage']}.json"
                )
                row["output_path"] = repo_display_path(output_path)
            append_jsonl(out_path, row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk-run", type=Path, action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--run-label", required=True)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--treatments", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    missing_runs = [str(run) for run in args.chunk_run if not run.exists()]
    if missing_runs:
        raise FileNotFoundError(f"missing chunk runs: {', '.join(missing_runs)}")

    if args.out.exists():
        if not args.force:
            raise FileExistsError(f"{args.out} already exists; pass --force to replace it")
        shutil.rmtree(args.out)
    args.out.mkdir(parents=True)

    transcripts = _copy_transcripts(args.chunk_run, args.out)
    _merge_jsonl(args.chunk_run, args.out / "assignment.jsonl", "assignment.jsonl")
    _merge_jsonl(args.chunk_run, args.out / "call_plan.jsonl", "call_plan.jsonl")
    _merge_jsonl(args.chunk_run, args.out / "case_scores.jsonl", "case_scores.jsonl")
    shutil.copyfile(args.cases, args.out / "selected_cases.jsonl")

    write_json(args.out / "metrics.json", aggregate_metrics(transcripts))
    write_json(
        args.out / "selection.json",
        {
            "source": str(args.cases),
            "selection_method": "combined_chunk_case_file",
            "case_count": len(_load_jsonl(args.cases)),
        },
    )
    write_json(
        args.out / "run_metadata.json",
        {
            "run_label": args.run_label,
            "execution_mode": "parallel_chunk_combined",
            "chunk_runs": [str(run) for run in args.chunk_run],
            "cases": str(args.cases),
            "treatments": str(args.treatments),
            "manifest": str(args.manifest),
            "transcript_count": len(transcripts),
        },
    )
    print(json.dumps({"transcript_count": len(transcripts)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
