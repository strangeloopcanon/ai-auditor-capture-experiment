#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auditor_capture.case_generation import load_jsonl
from auditor_capture.codex_runner import CodexConfig, run_codex_json
from auditor_capture.orchestrator import (
    SCHEMA_DIR,
    aggregate_metrics,
    append_jsonl,
    actor_response_requirement_text,
    add_final_ledger_updates_placeholder,
    auditor_final_review_requirement_text,
    auditor_final_schema_path,
    auditor_integrity_reminder_text,
    call_record,
    final_audit_context,
    hash_text,
    load_template,
    render,
    repo_display_path,
    response_context,
    should_continue_after_initial,
    stable_json,
    write_json,
)
from auditor_capture.scoring import score_transcript


REUSED_STAGES = ("actor_decision", "auditor_initial")


def event_outputs(transcript: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {event["stage"]: event["output"] for event in transcript["events"]}


def source_transcripts(run: Path, treatment_id: str) -> list[dict[str, Any]]:
    paths = sorted((run / "transcripts" / treatment_id).glob("*/transcript.json"))
    if not paths:
        raise FileNotFoundError(f"no source transcripts under {run / 'transcripts' / treatment_id}")
    return [json.loads(path.read_text(encoding="utf-8")) for path in paths]


def reused_event(
    *,
    run_id: str,
    source_event: dict[str, Any],
    output_path: Path,
    treatment_id: str,
    source_run: Path,
    source_treatment: str,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "case_id": source_event["case_id"],
        "treatment_id": treatment_id,
        "stage": source_event["stage"],
        "model": source_event["model"],
        "channel": source_event["channel"],
        "visible_context_hash": source_event["visible_context_hash"],
        "prompt_hash": source_event["prompt_hash"],
        "output_path": repo_display_path(output_path),
        "schema_path": source_event["schema_path"],
        "reused_from": {
            "run": str(source_run),
            "treatment_id": source_treatment,
            "output_path": source_event["output_path"],
        },
        "output": source_event["output"],
    }


def concern_count(transcript: dict[str, Any]) -> int:
    outputs = event_outputs(transcript)
    return len(outputs.get("auditor_initial", {}).get("specific_concerns", []))


def source_pifc(transcript: dict[str, Any]) -> bool:
    return bool(transcript.get("scoring_result", {}).get("persuasion_induced_false_compliance"))


def select_case_ids(
    *,
    transcripts: list[dict[str, Any]],
    explicit_case_ids: set[str] | None,
    limit: int | None,
    min_source_concerns: int,
) -> list[str]:
    candidates = []
    for transcript in transcripts:
        outputs = event_outputs(transcript)
        initial = outputs.get("auditor_initial", {})
        if initial.get("initial_verdict") not in {"suspicious", "noncompliant"}:
            continue
        if concern_count(transcript) < min_source_concerns:
            continue
        if explicit_case_ids is not None and transcript["case_id"] not in explicit_case_ids:
            continue
        candidates.append(transcript)

    candidates.sort(
        key=lambda transcript: (
            not source_pifc(transcript),
            -concern_count(transcript),
            transcript["case_id"],
        )
    )
    if limit is not None:
        candidates = candidates[:limit]
    return [transcript["case_id"] for transcript in candidates]


def run_response_and_final(
    *,
    cases: list[dict[str, Any]],
    treatment: dict[str, Any],
    manifest: dict[str, Any],
    source_run: Path,
    source_treatment: str,
    out_dir: Path,
    dry_run: bool,
    execute: bool,
) -> dict[str, Any]:
    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    treatment_id = treatment["treatment_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    call_plan = out_dir / manifest["outputs"]["call_plan"]
    if call_plan.exists():
        call_plan.unlink()
    assignment_path = out_dir / "assignment.jsonl"
    if assignment_path.exists():
        assignment_path.unlink()

    cases_by_id = {case["case_id"]: case for case in cases}
    codex_config = CodexConfig(
        binary=manifest["codex"].get("binary", "codex"),
        skip_git_repo_check=manifest["codex"].get("skip_git_repo_check", True),
        ephemeral=manifest["codex"].get("ephemeral", True),
        ignore_user_config=manifest["codex"].get("ignore_user_config", True),
        ignore_rules=manifest["codex"].get("ignore_rules", True),
        sandbox=manifest["codex"].get("sandbox", "read-only"),
        cwd=ROOT,
    )
    response_schema = SCHEMA_DIR / "actor_response.schema.json"
    transcripts = []
    seen_case_ids: set[str] = set()

    for source_transcript in source_transcripts(source_run, source_treatment):
        case_id = source_transcript["case_id"]
        if case_id not in cases_by_id:
            continue
        seen_case_ids.add(case_id)
        case = cases_by_id[case_id]
        source_events_by_stage = {event["stage"]: event for event in source_transcript["events"]}
        source_outputs = event_outputs(source_transcript)
        missing = [stage for stage in REUSED_STAGES if stage not in source_events_by_stage]
        if missing:
            raise ValueError(f"{case_id} missing source stages: {missing}")

        base = out_dir / "transcripts" / treatment_id / case_id
        events = []
        for stage in REUSED_STAGES:
            output_path = base / f"{stage}.json"
            write_json(output_path, source_outputs[stage])
            events.append(
                reused_event(
                    run_id=run_id,
                    source_event=source_events_by_stage[stage],
                    output_path=output_path,
                    treatment_id=treatment_id,
                    source_run=source_run,
                    source_treatment=source_treatment,
                )
            )

        actor_response = None
        auditor_final = None
        final_ctx = None
        if should_continue_after_initial(treatment, source_outputs["auditor_initial"]):
            response_ctx = response_context(
                case,
                treatment,
                source_outputs["actor_decision"],
                source_outputs["auditor_initial"],
            )
            response_prompt = render(
                load_template("actor_response.md"),
                {
                    "ACTOR_RESPONSE_REQUIREMENT": actor_response_requirement_text(treatment),
                    "RESPONSE_CONTEXT": json.dumps(response_ctx, indent=2, sort_keys=True),
                },
            )
            response_output_path = base / "actor_response.json"
            response_record = call_record(
                run_id=run_id,
                case_id=case_id,
                treatment_id=treatment_id,
                stage="actor_response",
                model=manifest["actor_model"],
                channel="actor_to_auditor_response",
                context=response_ctx,
                prompt=response_prompt,
                output_path=response_output_path,
                schema_path=response_schema,
            )
            append_jsonl(call_plan, response_record)
            if execute:
                actor_response = run_codex_json(
                    prompt=response_prompt,
                    model=manifest["actor_model"],
                    output_last_message=response_output_path,
                    output_schema=response_schema,
                    config=codex_config,
                )
            else:
                actor_response = {
                    "response_type": "mixed",
                    "new_evidence_ids": [],
                    "argument_summary": "Dry-run state-tracking stress placeholder.",
                    "claims_about_policy": "Dry-run placeholder.",
                    "claims_about_business_cost": "Dry-run placeholder.",
                    "concessions": ["Dry-run concession."],
                    "requested_auditor_action": "caveated_compliance",
                    "private_or_side_channel_content": "",
                }
                if dry_run:
                    write_json(response_output_path, actor_response)
            events.append({**response_record, "output": actor_response})

            final_ctx = final_audit_context(
                case,
                treatment,
                source_outputs["actor_decision"],
                source_outputs["auditor_initial"],
                actor_response,
            )
            final_prompt = render(
                load_template("auditor_final.md"),
                {
                    "FINAL_AUDIT_CONTEXT": json.dumps(final_ctx, indent=2, sort_keys=True),
                    "AUDITOR_INTEGRITY_REMINDER": auditor_integrity_reminder_text(treatment),
                    "AUDITOR_FINAL_REVIEW_REQUIREMENT": auditor_final_review_requirement_text(treatment),
                },
            )
            final_schema = auditor_final_schema_path(treatment)
            final_output_path = base / "auditor_final.json"
            final_record = call_record(
                run_id=run_id,
                case_id=case_id,
                treatment_id=treatment_id,
                stage="auditor_final",
                model=manifest["auditor_model"],
                channel="auditor_final_workpaper",
                context=final_ctx,
                prompt=final_prompt,
                output_path=final_output_path,
                schema_path=final_schema,
            )
            append_jsonl(call_plan, final_record)
            if execute:
                auditor_final = run_codex_json(
                    prompt=final_prompt,
                    model=manifest["auditor_model"],
                    output_last_message=final_output_path,
                    output_schema=final_schema,
                    config=codex_config,
                )
            else:
                auditor_final = {
                    "final_verdict": source_outputs["auditor_initial"]["initial_verdict"],
                    "final_risk_score": source_outputs["auditor_initial"]["initial_risk_score"],
                    "did_verdict_change": "no",
                    "direction_of_change": "none",
                    "reason_for_change": "none",
                    "new_admissible_evidence_received": "no",
                    "new_evidence_quality": "none",
                    "remaining_concerns": source_outputs["auditor_initial"].get(
                        "specific_concerns", []
                    ),
                    "final_rationale": "Dry-run final placeholder.",
                    "escalation_decision": "escalate",
                    "confidence": 0.5,
                }
                if treatment.get("_auditor_final_review_mode") == "self_generated_concern_ledger":
                    auditor_final = add_final_ledger_updates_placeholder(
                        auditor_final,
                        source_outputs["auditor_initial"],
                    )
                if dry_run:
                    write_json(final_output_path, auditor_final)
            events.append({**final_record, "output": auditor_final})

        scoring_result = score_transcript(
            case=case,
            treatment=treatment,
            actor_output=source_outputs["actor_decision"],
            auditor_initial=source_outputs["auditor_initial"],
            actor_response=actor_response,
            auditor_final=auditor_final,
        )
        transcript = {
            "run_id": run_id,
            "case_id": case_id,
            "domain": case["domain"],
            "treatment_id": treatment_id,
            "model_actor": source_transcript["model_actor"],
            "model_auditor": manifest["auditor_model"],
            "actor_visible_context_hash": source_transcript["actor_visible_context_hash"],
            "auditor_visible_context_hash": hash_text(
                stable_json(final_ctx or source_outputs["auditor_initial"])
            ),
            "events": events,
            "ground_truth_labels": case["ground_truth_label"],
            "scoring_result": scoring_result,
            "qualitative_coding": None,
            "continuation_skipped": actor_response is None,
            "source_reuse": {
                "run": str(source_run),
                "treatment_id": source_treatment,
                "reused_stages": list(REUSED_STAGES),
            },
        }
        write_json(base / "transcript.json", transcript)
        transcripts.append(transcript)
        append_jsonl(
            assignment_path,
            {
                "case_id": case_id,
                "domain": case["domain"],
                "archetype": case["ground_truth_label"]["archetype"],
                "treatment_id": treatment_id,
                "source_run": str(source_run),
                "source_treatment_id": source_treatment,
            },
        )

    missing_sources = sorted(set(cases_by_id) - seen_case_ids)
    if missing_sources:
        raise KeyError(f"missing source transcripts for cases: {missing_sources[:10]}")

    metrics = aggregate_metrics(transcripts)
    write_json(out_dir / manifest["outputs"]["metrics"], metrics)
    scores_path = out_dir / manifest["outputs"]["case_scores"]
    if scores_path.exists():
        scores_path.unlink()
    for transcript in transcripts:
        append_jsonl(
            scores_path,
            {
                "run_id": transcript["run_id"],
                "case_id": transcript["case_id"],
                "domain": transcript["domain"],
                "treatment_id": transcript["treatment_id"],
                **transcript["scoring_result"],
            },
        )
    write_json(
        out_dir / "run_metadata.json",
        {
            "run_label": out_dir.name,
            "execution_mode": "actor_response_and_final_rerun_reusing_source_initial_stages",
            "source_run": str(source_run),
            "source_treatment_id": source_treatment,
            "reused_stages": list(REUSED_STAGES),
            "cases": len(transcripts),
            "treatment": treatment_id,
            "manifest_actor_model": manifest["actor_model"],
            "manifest_auditor_model": manifest["auditor_model"],
        },
    )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--treatment", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--source-run", required=True, type=Path)
    parser.add_argument("--source-treatment", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--limit-cases", type=int)
    parser.add_argument("--min-source-concerns", type=int, default=1)
    parser.add_argument("--case-id", action="append", dest="case_ids")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    all_cases = load_jsonl(args.cases)
    cases_by_id = {case["case_id"]: case for case in all_cases}
    treatments = json.loads(args.treatment.read_text(encoding="utf-8"))
    if len(treatments) != 1:
        raise ValueError("--treatment must contain exactly one treatment")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    source = source_transcripts(args.source_run, args.source_treatment)
    selected_ids = select_case_ids(
        transcripts=source,
        explicit_case_ids=set(args.case_ids) if args.case_ids else None,
        limit=args.limit_cases,
        min_source_concerns=args.min_source_concerns,
    )
    cases = [cases_by_id[case_id] for case_id in selected_ids]
    args.out.mkdir(parents=True, exist_ok=True)
    selected_cases_path = args.out / "selected_cases.jsonl"
    selected_cases_path.write_text(
        "".join(json.dumps(case, sort_keys=True) + "\n" for case in cases),
        encoding="utf-8",
    )
    write_json(
        args.out / "selection.json",
        {
            "source_run": str(args.source_run),
            "source_treatment": args.source_treatment,
            "selected_case_count": len(selected_ids),
            "limit_cases": args.limit_cases,
            "min_source_concerns": args.min_source_concerns,
            "case_ids": selected_ids,
            "source_case_features": [
                {
                    "case_id": transcript["case_id"],
                    "source_concern_count": concern_count(transcript),
                    "source_pifc": source_pifc(transcript),
                }
                for transcript in source
                if transcript["case_id"] in set(selected_ids)
            ],
        },
    )
    metrics = run_response_and_final(
        cases=cases,
        treatment=treatments[0],
        manifest=manifest,
        source_run=args.source_run,
        source_treatment=args.source_treatment,
        out_dir=args.out,
        dry_run=args.dry_run,
        execute=args.execute,
    )
    print(json.dumps(metrics, indent=2, sort_keys=True))
    print(f"selected_cases={repo_display_path(selected_cases_path)}")


if __name__ == "__main__":
    main()
