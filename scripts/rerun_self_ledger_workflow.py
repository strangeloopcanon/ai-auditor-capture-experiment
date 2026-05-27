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
    aggregate_metrics,
    append_jsonl,
    actor_response_requirement_text,
    add_final_ledger_updates_placeholder,
    add_initial_ledger_placeholder,
    audit_context,
    auditor_final_review_requirement_text,
    auditor_final_schema_path,
    auditor_initial_review_requirement_text,
    auditor_initial_schema_path,
    auditor_integrity_reminder_text,
    call_record,
    final_audit_context,
    hash_text,
    load_template,
    placeholder_output,
    render,
    repo_display_path,
    response_context,
    should_continue_after_initial,
    stable_json,
    write_json,
)
from auditor_capture.scoring import score_transcript


def event_outputs(transcript: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {event["stage"]: event["output"] for event in transcript["events"]}


def source_transcripts(run: Path, treatment_id: str) -> dict[str, dict[str, Any]]:
    paths = sorted((run / "transcripts" / treatment_id).glob("*/transcript.json"))
    if not paths:
        raise FileNotFoundError(f"no source transcripts under {run / 'transcripts' / treatment_id}")
    transcripts = {}
    for path in paths:
        transcript = json.loads(path.read_text(encoding="utf-8"))
        transcripts[transcript["case_id"]] = transcript
    return transcripts


def reused_actor_event(
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


def copied_event(
    *,
    run_id: str,
    source_event: dict[str, Any],
    output_path: Path,
    treatment_id: str,
    shared_from_treatment: str,
) -> dict[str, Any]:
    event = dict(source_event)
    event["run_id"] = run_id
    event["treatment_id"] = treatment_id
    event["output_path"] = repo_display_path(output_path)
    event["reused_from"] = {
        "same_run_treatment_id": shared_from_treatment,
        "stage": source_event["stage"],
        "case_id": source_event["case_id"],
    }
    return event


def run_workflow(
    *,
    cases: list[dict[str, Any]],
    treatments: list[dict[str, Any]],
    manifest: dict[str, Any],
    source_run: Path,
    source_treatment: str,
    out_dir: Path,
    dry_run: bool,
    execute: bool,
) -> dict[str, Any]:
    if not treatments:
        raise ValueError("at least one treatment is required")
    interaction_treatment = treatments[0]
    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        out_dir / "selection.json",
        {
            "source_run": str(source_run),
            "source_treatment": source_treatment,
            "selected_case_count": len(cases),
            "case_ids": [case["case_id"] for case in cases],
        },
    )
    (out_dir / "selected_cases.jsonl").write_text(
        "".join(json.dumps(case, sort_keys=True) + "\n" for case in cases),
        encoding="utf-8",
    )
    call_plan = out_dir / manifest["outputs"]["call_plan"]
    if call_plan.exists():
        call_plan.unlink()
    assignment_path = out_dir / "assignment.jsonl"
    if assignment_path.exists():
        assignment_path.unlink()

    source_by_case = source_transcripts(source_run, source_treatment)
    codex_config = CodexConfig(
        binary=manifest["codex"].get("binary", "codex"),
        skip_git_repo_check=manifest["codex"].get("skip_git_repo_check", True),
        ephemeral=manifest["codex"].get("ephemeral", True),
        ignore_user_config=manifest["codex"].get("ignore_user_config", True),
        ignore_rules=manifest["codex"].get("ignore_rules", True),
        sandbox=manifest["codex"].get("sandbox", "read-only"),
        cwd=ROOT,
    )

    transcripts: list[dict[str, Any]] = []
    for case in cases:
        case_id = case["case_id"]
        if case_id not in source_by_case:
            raise KeyError(f"missing source transcript for case: {case_id}")
        source_transcript = source_by_case[case_id]
        source_events_by_stage = {event["stage"]: event for event in source_transcript["events"]}
        source_outputs = event_outputs(source_transcript)
        if "actor_decision" not in source_events_by_stage:
            raise ValueError(f"{case_id} missing source actor_decision")

        shared_treatment_id = interaction_treatment["treatment_id"]
        shared_base = out_dir / "transcripts" / shared_treatment_id / case_id
        actor_output_path = shared_base / "actor_decision.json"
        write_json(actor_output_path, source_outputs["actor_decision"])
        actor_event = reused_actor_event(
            run_id=run_id,
            source_event=source_events_by_stage["actor_decision"],
            output_path=actor_output_path,
            treatment_id=shared_treatment_id,
            source_run=source_run,
            source_treatment=source_treatment,
        )

        initial_context = audit_context(case, interaction_treatment, source_outputs["actor_decision"])
        initial_prompt = render(
            load_template("auditor_initial.md"),
            {
                "AUDIT_CONTEXT": json.dumps(initial_context, indent=2, sort_keys=True),
                "AUDITOR_INTEGRITY_REMINDER": auditor_integrity_reminder_text(interaction_treatment),
                "AUDITOR_INITIAL_REVIEW_REQUIREMENT": auditor_initial_review_requirement_text(
                    interaction_treatment
                ),
            },
        )
        initial_schema = auditor_initial_schema_path(interaction_treatment)
        initial_output_path = shared_base / "auditor_initial.json"
        initial_record = call_record(
            run_id=run_id,
            case_id=case_id,
            treatment_id=shared_treatment_id,
            stage="auditor_initial",
            model=manifest["auditor_model"],
            channel="auditor_private_workpaper",
            context=initial_context,
            prompt=initial_prompt,
            output_path=initial_output_path,
            schema_path=initial_schema,
        )
        append_jsonl(call_plan, initial_record)
        if execute:
            auditor_initial = run_codex_json(
                prompt=initial_prompt,
                model=manifest["auditor_model"],
                output_last_message=initial_output_path,
                output_schema=initial_schema,
                config=codex_config,
            )
        else:
            auditor_initial = placeholder_output("auditor_initial", case)
            if interaction_treatment.get("_auditor_initial_review_mode") == "self_generated_concern_ledger":
                auditor_initial = add_initial_ledger_placeholder(auditor_initial)
            if dry_run:
                write_json(initial_output_path, auditor_initial)
        initial_event = {**initial_record, "output": auditor_initial}

        actor_response = None
        response_event = None
        if should_continue_after_initial(interaction_treatment, auditor_initial):
            response_ctx = response_context(
                case,
                interaction_treatment,
                source_outputs["actor_decision"],
                auditor_initial,
            )
            response_prompt = render(
                load_template("actor_response.md"),
                {
                    "ACTOR_RESPONSE_REQUIREMENT": actor_response_requirement_text(interaction_treatment),
                    "RESPONSE_CONTEXT": json.dumps(response_ctx, indent=2, sort_keys=True),
                },
            )
            response_schema = ROOT / "schemas" / "actor_response.schema.json"
            response_output_path = shared_base / "actor_response.json"
            response_record = call_record(
                run_id=run_id,
                case_id=case_id,
                treatment_id=shared_treatment_id,
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
                actor_response = placeholder_output("actor_response", case)
                if dry_run:
                    write_json(response_output_path, actor_response)
            response_event = {**response_record, "output": actor_response}

        for treatment in treatments:
            treatment_id = treatment["treatment_id"]
            base = out_dir / "transcripts" / treatment_id / case_id
            events = []
            actor_path = base / "actor_decision.json"
            initial_path = base / "auditor_initial.json"
            write_json(actor_path, source_outputs["actor_decision"])
            write_json(initial_path, auditor_initial)
            events.append(
                copied_event(
                    run_id=run_id,
                    source_event=actor_event,
                    output_path=actor_path,
                    treatment_id=treatment_id,
                    shared_from_treatment=shared_treatment_id,
                )
            )
            events.append(
                copied_event(
                    run_id=run_id,
                    source_event=initial_event,
                    output_path=initial_path,
                    treatment_id=treatment_id,
                    shared_from_treatment=shared_treatment_id,
                )
            )

            auditor_final = None
            final_ctx = None
            if actor_response is not None and response_event is not None:
                response_path = base / "actor_response.json"
                write_json(response_path, actor_response)
                events.append(
                    copied_event(
                        run_id=run_id,
                        source_event=response_event,
                        output_path=response_path,
                        treatment_id=treatment_id,
                        shared_from_treatment=shared_treatment_id,
                    )
                )
                final_ctx = final_audit_context(
                    case,
                    treatment,
                    source_outputs["actor_decision"],
                    auditor_initial,
                    actor_response,
                )
                final_prompt = render(
                    load_template("auditor_final.md"),
                    {
                        "FINAL_AUDIT_CONTEXT": json.dumps(final_ctx, indent=2, sort_keys=True),
                        "AUDITOR_INTEGRITY_REMINDER": auditor_integrity_reminder_text(treatment),
                        "AUDITOR_FINAL_REVIEW_REQUIREMENT": auditor_final_review_requirement_text(
                            treatment
                        ),
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
                    auditor_final = placeholder_output("auditor_final", case)
                    if treatment.get("_auditor_final_review_mode") == "self_generated_concern_ledger":
                        auditor_final = add_final_ledger_updates_placeholder(
                            auditor_final,
                            auditor_initial,
                        )
                    if dry_run:
                        write_json(final_output_path, auditor_final)
                events.append({**final_record, "output": auditor_final})

            scoring_result = score_transcript(
                case=case,
                treatment=treatment,
                actor_output=source_outputs["actor_decision"],
                auditor_initial=auditor_initial,
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
                    stable_json(final_ctx or initial_context)
                ),
                "events": events,
                "ground_truth_labels": case["ground_truth_label"],
                "scoring_result": scoring_result,
                "qualitative_coding": None,
                "continuation_skipped": actor_response is None,
                "source_reuse": {
                    "run": str(source_run),
                    "treatment_id": source_treatment,
                    "reused_stages": ["actor_decision"],
                    "rerun_stages": ["auditor_initial", "actor_response", "auditor_final"],
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
            "execution_mode": "self_ledger_workflow_reusing_actor_decision",
            "source_run": str(source_run),
            "source_treatment_id": source_treatment,
            "reused_stages": ["actor_decision"],
            "rerun_stages": ["auditor_initial", "actor_response", "auditor_final"],
            "cases": len(cases),
            "treatments": [treatment["treatment_id"] for treatment in treatments],
            "manifest_actor_model": manifest["actor_model"],
            "manifest_auditor_model": manifest["auditor_model"],
        },
    )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument("--treatments", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--source-run", required=True, type=Path)
    parser.add_argument("--source-treatment", required=True)
    parser.add_argument("--out", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    treatments = json.loads(args.treatments.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    cases = load_jsonl(args.cases)
    metrics = run_workflow(
        cases=cases,
        treatments=treatments,
        manifest=manifest,
        source_run=args.source_run,
        source_treatment=args.source_treatment,
        out_dir=args.out,
        dry_run=args.dry_run,
        execute=args.execute,
    )
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
