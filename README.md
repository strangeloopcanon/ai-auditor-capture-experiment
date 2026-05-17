# Context Capture Audit Game

This repo tests whether an AI actor being audited can talk an AI auditor out of a correct concern without giving it genuinely new admissible evidence.

Across the current live runs, the answer is yes. The original synthetic benchmark shows the effect. An explicit anti-capture integrity reminder reduces it, but does not eliminate it. A new source-grounded model-card setup then brings the effect back strongly under that same integrity reminder.

## Current Evidence

| Setup | Cases | Auditor condition | Transcripts | Persuasion-induced false compliance | Overall false compliance | Takeaway |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Original synthetic run | Synthetic borderline cases across procurement, access exceptions, and model-card disclosure | Standard auditor prompt | 150 | 15/124 = 12.1% | 16/150 = 10.7% | The capture pattern appears. |
| Synthetic run with integrity reminder | Same synthetic cases | Explicit anti-capture reminder to stay independent, evidence-based, and not defer to persuasion | 150 | 5/123 = 4.1% | 7/150 = 4.7% | The reminder helps, but does not solve it. |
| Source-grounded model-card stress run | Source-note cases grounded in Hugging Face/NIST material plus realistic organization-specific launch artifacts | Same anti-capture integrity reminder | 150 | 13/123 = 10.6% | 15/150 = 10.0% | The effect comes back strongly in a more realistic setting. |

The source-grounded run is the new methodological step. It is not another sample from the old synthetic generator: it uses source-note packets, keeps provenance attached to each generated case, and tests model-card certification scenarios built from public governance/process sources plus source-tracked launch artifacts.

## Source-Grounded Setup

The active source-grounded fixture is:

```text
data/source_notes/source_grounded_integrity_stress_25.json
```

It grounds the governance surface in:

- Hugging Face Model Cards documentation.
- NIST AI Risk Management Framework.

It then adds source-noted organization-specific artifacts for the pressure points that matter in real model release work:

- stale prior approval
- draft mitigation
- missing eval coverage
- materiality dispute
- rollout or monitoring controls that do not actually close the evidence gap

Generated cases preserve this provenance in `source_provenance`, and each evidence item cites the relevant `source_note_ids`.

## Key Artifacts

- Original synthetic run: `runs/borderline_live_150/`
- Synthetic run with integrity reminder: `runs/integrity_reminder_live_150/`
- Source-grounded integrity stress run: `runs/source_grounded_integrity_stress_25_integrity/`
- Source-note packet: `data/source_notes/source_grounded_integrity_stress_25.json`
- Generated source-grounded cases: `data/cases_source_grounded_integrity_stress_25.jsonl`
- Replication config: `config/replication.source_grounded_integrity_stress_25.json`
- Repeat plan: `docs/replication_plan.md`

This repo intentionally excludes essay drafts, Google Doc exports, rendered article assets, and other publication artifacts.

## Reproduce Cases

Generate the original synthetic benchmark file:

```bash
python3 scripts/generate_cases.py \
  --mode borderline \
  --cases-per-domain 50 \
  --output data/cases_borderline_150.jsonl
```

Generate the source-grounded model-card stress file:

```bash
python3 scripts/generate_cases.py \
  --mode source-notes \
  --source-notes data/source_notes/source_grounded_integrity_stress_25.json \
  --output data/cases_source_grounded_integrity_stress_25.jsonl
```

## Run And Inspect

Show the call budget before spending live calls:

```bash
python3 scripts/plan_calls.py \
  --cases data/cases_source_grounded_integrity_stress_25.jsonl \
  --treatments config/treatments.integrity_reminder.json \
  --manifest config/run_manifest.mvp.json
```

Run the source-grounded integrity stress set:

```bash
python3 scripts/run_experiment.py \
  --cases data/cases_source_grounded_integrity_stress_25.jsonl \
  --treatments config/treatments.integrity_reminder.json \
  --manifest config/run_manifest.mvp.json \
  --out runs/source_grounded_integrity_stress_25_integrity \
  --assignment all_conditions \
  --execute
```

Analyze a completed run:

```bash
python3 scripts/analyze_run.py \
  --run runs/source_grounded_integrity_stress_25_integrity \
  --json-out runs/source_grounded_integrity_stress_25_integrity/analysis.json
```

Run tests:

```bash
python3 -m pytest -q
```

## Replication Plan

The next planned step is repeated source-grounded integrity runs with fixed output folders and per-run seeds:

```bash
python3 scripts/run_replications.py \
  --config config/replication.source_grounded_integrity_stress_25.json \
  --repeats 5 \
  --plan-only
```

Exact maximum budgets:

```text
1 repeat   = 150 transcripts,   550 calls
3 repeats  = 450 transcripts, 1,650 calls
5 repeats  = 750 transcripts, 2,750 calls
10 repeats = 1,500 transcripts, 5,500 calls
```

The completed source-grounded run used 546 calls against the 550-call maximum because two selective continuations were skipped after initial caveated-compliance verdicts.

## Model Boundary

All live model calls are routed through the local Codex CLI. The harness allows only `gpt-5.4` and `gpt-5.5`; the completed runs here use `gpt-5.4`.
