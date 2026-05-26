#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auditor_capture.call_budget import plan_budget
from auditor_capture.case_generation import load_jsonl
from auditor_capture.orchestrator import run_experiment


RUN_SPECS: dict[str, dict[str, Any]] = {
    "source_grounded_stress_no_integrity_fixed_25": {
        "question": "Source-grounded stress cases without the auditor integrity reminder, using the fixed actor-visible treatment boundary.",
        "cases": "data/cases_source_grounded_integrity_stress_25.jsonl",
        "treatments": "config/treatments.borderline.json",
        "manifest": "config/run_manifest.mvp.json",
        "out": "runs/source_grounded_stress_no_integrity_fixed_25",
        "assignment": "all_conditions",
        "chunk_size": 5,
    },
    "source_grounded_stress_integrity_fixed_25": {
        "question": "Source-grounded stress cases with the auditor integrity reminder, rerun under the fixed actor-visible treatment boundary.",
        "cases": "data/cases_source_grounded_integrity_stress_25.jsonl",
        "treatments": "config/treatments.integrity_reminder.json",
        "manifest": "config/run_manifest.mvp.json",
        "out": "runs/source_grounded_stress_integrity_fixed_25",
        "assignment": "all_conditions",
        "chunk_size": 5,
    },
    "raw_vs_summary_original_cases_fixed_150": {
        "question": "Phase 3 original 150 source-grounded cases rerun under the fixed actor-visible treatment boundary.",
        "cases": "data/cases_source_grounded_raw_access_ab_150.jsonl",
        "treatments": "config/treatments.raw_vs_summary_neutral_integrity.json",
        "manifest": "config/run_manifest.mvp.json",
        "out": "runs/source_grounded_raw_vs_summary_original_cases_fixed_150",
        "assignment": "all_conditions",
        "chunk_size": 30,
    },
    "raw_access_actor_knowledge_fixed_150": {
        "question": "Phase 4 raw-access actor-knowledge A/B rerun under the fixed actor-visible treatment boundary.",
        "cases": "data/cases_source_grounded_raw_access_ab_150.jsonl",
        "treatments": "config/treatments.raw_access_ab_integrity.json",
        "manifest": "config/run_manifest.mvp.json",
        "out": "runs/source_grounded_raw_access_ab_fixed_150",
        "assignment": "all_conditions",
        "chunk_size": 30,
    },
}

GROUPS = {
    "all": tuple(RUN_SPECS),
    "source-grounded-reminder": (
        "source_grounded_stress_no_integrity_fixed_25",
        "source_grounded_stress_integrity_fixed_25",
    ),
    "phase3": ("raw_vs_summary_original_cases_fixed_150",),
    "phase4": ("raw_access_actor_knowledge_fixed_150",),
}

COMPARISONS = [
    {
        "id": "source_grounded_raw_vs_summary_original_cases_fixed_150",
        "question": "Phase 3 original cases after actor-visible treatment boundary fix",
        "left_label": "Raw evidence",
        "left_run": "runs/source_grounded_raw_vs_summary_original_cases_fixed_150",
        "left_treatment": "H3_raw_hidden_access_integrity",
        "right_label": "Summary only",
        "right_run": "runs/source_grounded_raw_vs_summary_original_cases_fixed_150",
        "right_treatment": "RVS1_summary_not_disclosed_integrity",
        "out": "runs/source_grounded_raw_vs_summary_original_cases_fixed_150_comparison",
        "required_runs": ("raw_vs_summary_original_cases_fixed_150",),
    },
    {
        "id": "source_grounded_raw_access_ab_fixed_150",
        "question": "Phase 4 actor told vs not told after actor-visible treatment boundary fix",
        "left_label": "Raw access not told",
        "left_run": "runs/source_grounded_raw_access_ab_fixed_150",
        "left_treatment": "H3_raw_hidden_access_integrity",
        "right_label": "Raw access told",
        "right_run": "runs/source_grounded_raw_access_ab_fixed_150",
        "right_treatment": "H4_raw_known_access_integrity",
        "out": "runs/source_grounded_raw_access_ab_fixed_150_comparison",
        "required_runs": ("raw_access_actor_knowledge_fixed_150",),
    },
]


def resolve(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def repo_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path_text: str) -> Any:
    return json.loads(resolve(path_text).read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_plan(selected: list[str]) -> dict[str, Any]:
    runs = []
    for run_key in selected:
        spec = RUN_SPECS[run_key]
        cases = load_jsonl(resolve(spec["cases"]))
        treatments = load_json(spec["treatments"])
        manifest = load_json(spec["manifest"])
        budget = plan_budget(
            len(cases),
            treatments,
            include_appeals_judge=bool(manifest.get("include_appeals_judge", False)),
        )
        runs.append(
            {
                "run_key": run_key,
                "question": spec["question"],
                "cases": spec["cases"],
                "case_count": len(cases),
                "treatments": spec["treatments"],
                "treatment_count": len(treatments),
                "manifest": spec["manifest"],
                "out": spec["out"],
                "assignment": spec["assignment"],
                "expected_transcripts": len(cases) * len(treatments),
                "max_calls": budget["total_calls"],
                "budget": budget,
            }
        )
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "selected": selected,
        "total_expected_transcripts": sum(run["expected_transcripts"] for run in runs),
        "total_max_calls": sum(run["max_calls"] for run in runs),
        "runs": runs,
    }


def ensure_clean_output(out_dir: Path, *, overwrite: bool) -> None:
    if not out_dir.exists() or not any(out_dir.iterdir()):
        return
    if not overwrite:
        raise FileExistsError(f"{repo_path(out_dir)} already exists; pass --overwrite to replace it.")
    if out_dir.resolve() == ROOT.resolve() or ROOT.resolve() not in out_dir.resolve().parents:
        raise ValueError(f"Refusing to overwrite non-repo output dir: {out_dir}")
    if out_dir.parts[-2] != "runs" and "runs" not in out_dir.parts:
        raise ValueError(f"Refusing to overwrite output outside runs/: {out_dir}")
    shutil.rmtree(out_dir)


def analyze_run(out_dir: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "analyze_run.py"),
            "--run",
            str(out_dir),
            "--json-out",
            str(out_dir / "analysis.json"),
            "--md-out",
            str(out_dir / "analysis.md"),
        ],
        check=True,
    )


def write_case_chunks(run_key: str, cases: list[dict[str, Any]], chunk_size: int) -> list[Path]:
    chunks_dir = ROOT / ".codex" / "tmp" / "methodology_rerun_case_chunks" / run_key
    if chunks_dir.exists():
        shutil.rmtree(chunks_dir)
    chunks_dir.mkdir(parents=True)
    paths = []
    for index, start in enumerate(range(0, len(cases), chunk_size), start=1):
        path = chunks_dir / f"cases_{index:03d}.jsonl"
        with path.open("w", encoding="utf-8") as handle:
            for case in cases[start : start + chunk_size]:
                handle.write(json.dumps(case, sort_keys=True) + "\n")
        paths.append(path)
    return paths


def run_chunk_processes(
    *,
    run_key: str,
    spec: dict[str, Any],
    case_chunks: list[Path],
    dry_run: bool,
    execute: bool,
    jobs: int,
    overwrite: bool,
) -> list[Path]:
    parts_root = ROOT / "runs" / "_methodology_rerun_parts" / run_key
    ensure_clean_output(parts_root, overwrite=overwrite)
    parts_root.mkdir(parents=True, exist_ok=True)
    mode_flag = "--execute" if execute else "--dry-run"
    pending = list(enumerate(case_chunks, start=1))
    running: list[tuple[int, Path, subprocess.Popen[str], Path]] = []
    completed: list[Path] = []

    def start_next() -> None:
        if not pending:
            return
        index, chunk_path = pending.pop(0)
        part_dir = parts_root / f"chunk_{index:03d}"
        log_path = parts_root / f"chunk_{index:03d}.log"
        command = [
            sys.executable,
            str(ROOT / "scripts" / "run_experiment.py"),
            "--cases",
            str(chunk_path),
            "--treatments",
            str(resolve(spec["treatments"])),
            "--manifest",
            str(resolve(spec["manifest"])),
            "--out",
            str(part_dir),
            "--assignment",
            spec["assignment"],
            mode_flag,
        ]
        log_handle = log_path.open("w", encoding="utf-8")
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
        )
        # Popen does not keep a reference to the redirected file object, so close
        # our descriptor after the child has inherited it.
        log_handle.close()
        running.append((index, part_dir, process, log_path))

    for _ in range(min(jobs, len(pending))):
        start_next()

    while running:
        index, part_dir, process, log_path = running.pop(0)
        returncode = process.wait()
        if returncode != 0:
            log_tail = log_path.read_text(encoding="utf-8")[-4000:] if log_path.exists() else ""
            raise RuntimeError(
                f"{run_key} chunk {index:03d} failed with exit code {returncode}. "
                f"Log tail:\n{log_tail}"
            )
        completed.append(part_dir)
        start_next()
    return completed


def combine_chunks(run_key: str, spec: dict[str, Any], chunk_runs: list[Path]) -> None:
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "combine_run_chunks.py"),
            "--out",
            str(resolve(spec["out"])),
            "--run-label",
            run_key,
            "--cases",
            spec["cases"],
            "--treatments",
            spec["treatments"],
            "--manifest",
            spec["manifest"],
            "--force",
            *[arg for chunk_run in chunk_runs for arg in ("--chunk-run", str(chunk_run))],
        ],
        cwd=ROOT,
        check=True,
    )


def run_comparison(comparison: dict[str, Any]) -> None:
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "compare_run_arms.py"),
            "--comparison-id",
            comparison["id"],
            "--question",
            comparison["question"],
            "--left-label",
            comparison["left_label"],
            "--left-run",
            str(resolve(comparison["left_run"])),
            "--left-treatment",
            comparison["left_treatment"],
            "--right-label",
            comparison["right_label"],
            "--right-run",
            str(resolve(comparison["right_run"])),
            "--right-treatment",
            comparison["right_treatment"],
            "--out",
            str(resolve(comparison["out"])),
        ],
        check=True,
    )


def run_spec(
    run_key: str,
    *,
    dry_run: bool,
    execute: bool,
    overwrite: bool,
    jobs: int,
    parallel_chunks: bool,
) -> dict[str, Any]:
    spec = RUN_SPECS[run_key]
    out_dir = resolve(spec["out"])
    ensure_clean_output(out_dir, overwrite=overwrite)
    cases = load_jsonl(resolve(spec["cases"]))
    treatments = load_json(spec["treatments"])
    manifest = load_json(spec["manifest"])
    metadata = {
        "run_key": run_key,
        "question": spec["question"],
        "cases": spec["cases"],
        "treatments": spec["treatments"],
        "manifest": spec["manifest"],
        "assignment": spec["assignment"],
        "mode": "execute" if execute else "dry_run",
        "actor_visible_treatment_boundary": "fixed: treatment_id, evidence_access, actor_auditor_access_disclosure, auditor_precommitment, actor_visibility, auditor_integrity_reminder, and selective_continuation are hidden from actor_decision.",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if parallel_chunks:
        case_chunks = write_case_chunks(run_key, cases, int(spec["chunk_size"]))
        chunk_runs = run_chunk_processes(
            run_key=run_key,
            spec=spec,
            case_chunks=case_chunks,
            dry_run=dry_run,
            execute=execute,
            jobs=jobs,
            overwrite=overwrite,
        )
        combine_chunks(run_key, spec, chunk_runs)
        metadata["execution_mode"] = "parallel_case_chunks"
        metadata["chunk_size"] = spec["chunk_size"]
        metadata["chunk_runs"] = [repo_path(path) for path in chunk_runs]
        metrics = load_json(f"{spec['out']}/metrics.json")
    else:
        write_json(out_dir / "run_metadata.json", metadata)
        metrics = run_experiment(
            cases=cases,
            treatments=treatments,
            manifest=manifest,
            out_dir=out_dir,
            dry_run=dry_run,
            execute=execute,
            assignment=spec["assignment"],
            assignment_seed=None,
        )
    analyze_run(out_dir)
    metadata["metrics"] = metrics
    metadata["completed_at"] = datetime.now(timezone.utc).isoformat()
    write_json(out_dir / "run_metadata.json", metadata)
    return {
        "run_key": run_key,
        "out": spec["out"],
        "analysis": f"{spec['out']}/analysis.json",
        "metrics": metrics,
    }


def selected_run_keys(which: str) -> list[str]:
    if which in GROUPS:
        return list(GROUPS[which])
    if which in RUN_SPECS:
        return [which]
    raise ValueError(f"Unknown selection: {which}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--which", choices=sorted((*GROUPS.keys(), *RUN_SPECS.keys())), default="all")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--parallel-chunks", action="store_true")
    parser.add_argument("--jobs", type=int, default=3)
    parser.add_argument(
        "--summary-out",
        help="Optional JSON path for the invocation summary. By default the summary is printed only.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan-only", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    selected = selected_run_keys(args.which)
    plan = build_plan(selected)
    if args.plan_only:
        print(json.dumps(plan, indent=2, sort_keys=True))
        return

    if args.jobs < 1:
        raise ValueError("--jobs must be positive.")

    summaries = [
        run_spec(
            run_key,
            dry_run=args.dry_run,
            execute=args.execute,
            overwrite=args.overwrite,
            jobs=args.jobs,
            parallel_chunks=args.parallel_chunks,
        )
        for run_key in selected
    ]
    for comparison in COMPARISONS:
        if all(run_key in selected for run_key in comparison["required_runs"]):
            run_comparison(comparison)

    summary = {
        "mode": "execute" if args.execute else "dry_run",
        "plan": plan,
        "runs": summaries,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    if args.summary_out:
        write_json(resolve(args.summary_out), summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
