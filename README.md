# Context Capture Audit Game

This repo contains the experiment kit for the AI auditor capture study. It is intentionally scoped to the experimental harness, prompts, schemas, case files, and run outputs. Essay drafts, Google Doc exports, generated images, and publication artifacts are not part of the repo.

The experiment asks whether an audited AI actor can make an AI auditor move from a correct concern to false compliance by reframing a borderline evidentiary gap without supplying genuinely new admissible evidence.

## What Is Included

- `auditor_capture/` - Python harness for case generation, call planning, orchestration, Codex execution, and deterministic scoring.
- `prompts/` - structured Actor, Auditor, Actor-response, Auditor-final, and optional Appeals Judge prompts.
- `schemas/` - JSON schemas for role outputs, transcripts, treatments, cases, and scoring results.
- `config/treatments.borderline.json` - canonical six-condition borderline treatment set.
- `config/treatments.integrity_reminder.json` - follow-up treatment set with the generic auditor integrity reminder.
- `data/cases_borderline_150.jsonl` - canonical 150-case borderline case file.
- `runs/borderline_live_150/` - canonical live 150-case `gpt-5.4` run.
- `runs/integrity_reminder_live_150/` - live 150-case integrity-reminder run.
- `docs/` - experiment design notes, VEI mapping, and call-budget notes.
- `tests/` - standard-library unit tests for generation, call budgeting, assignment, and scoring.

## What Is Not Included

This repository excludes the public essay drafts and publishing artifacts. In particular, generated Google Doc exports, docx/html renders, chart images for the essay, and narrative writeup drafts were removed before publishing.

## Current Model Boundary

All live model calls are routed through the local Codex CLI. The harness allows only `gpt-5.4` and `gpt-5.5`, and the completed runs here use `gpt-5.4`.

The route was sanity-checked locally on 2026-05-05 with one `gpt-5.4` and one `gpt-5.5` call. Those checks are not counted in the experiment runs.

## Completed Runs

### Canonical Borderline Run

Path: `runs/borderline_live_150/`

- 150 cases across procurement, access exceptions, and model-card disclosure.
- Balanced single-treatment assignment across six conditions.
- 548 live Codex role calls using `gpt-5.4`.
- 150/150 Actor packets were deterministically weakly supported.
- Initial Auditor verdicts: 148 suspicious, 1 noncompliant, 1 compliant with caveats.
- No-response false compliance: 0/25.
- Persuasion-induced false compliance: 15/124 = 12.1%.
- Overall false compliance: 16/150 = 10.7%.

Primary machine-readable outputs:

- `runs/borderline_live_150/metrics.json`
- `runs/borderline_live_150/analysis.json`
- `runs/borderline_live_150/case_scores.jsonl`
- `runs/borderline_live_150/transcripts/`

### Integrity-Reminder Run

Path: `runs/integrity_reminder_live_150/`

- Same 150-case setup with a generic auditor reminder to remain independent and evidence-based.
- No-response false compliance: 0/25.
- Persuasion-induced false compliance: 5/123 = 4.1%.
- Overall false compliance: 7/150 = 4.7%.

Primary machine-readable outputs:

- `runs/integrity_reminder_live_150/metrics.json`
- `runs/integrity_reminder_live_150/analysis.json`
- `runs/integrity_reminder_live_150/case_scores.jsonl`
- `runs/integrity_reminder_live_150/transcripts/`

## Quick Start

Generate the canonical 150-case borderline file:

```bash
python3 scripts/generate_cases.py \
  --mode borderline \
  --cases-per-domain 50 \
  --output data/cases_borderline_150.jsonl
```

Show the call budget before spending any live calls:

```bash
python3 scripts/plan_calls.py \
  --cases data/cases_borderline_150.jsonl \
  --treatments config/treatments.borderline.json \
  --manifest config/run_manifest.mvp.json
```

Run the canonical balanced version:

```bash
python3 scripts/run_experiment.py \
  --cases data/cases_borderline_150.jsonl \
  --treatments config/treatments.borderline.json \
  --manifest config/run_manifest.mvp.json \
  --out runs/borderline_live_150 \
  --assignment balanced-stratified \
  --execute
```

Analyze a completed run:

```bash
python3 scripts/analyze_run.py runs/borderline_live_150
```

Run tests:

```bash
python3 -m pytest -q
```

## Call Budget

For the six canonical borderline conditions:

- No-response condition: 2 calls per assigned case.
- Response condition: 4 calls per assigned case.
- Optional Appeals Judge: +1 call per assigned case.
- Deterministic Regulator: 0 calls.

Balanced single-treatment assignment:

- 150-case run: up to 550 Codex LLM calls.
- The canonical run used 548 because one selective response stage was skipped after an initial caveated-compliance verdict.

Full Cartesian design across all six canonical conditions:

- 150 cases x all treatments: 3,300 Codex LLM calls.

The repo keeps the balanced runs because they are the cost-controlled experimental artifacts behind the essay.
