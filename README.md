# Context Capture Audit Game

This repository tests whether an AI actor being audited can persuade an AI auditor to soften a correct concern without providing genuinely new admissible evidence.

The benchmark has two parts: an initial synthetic stress test and a source-grounded model-card lane that attaches provenance to each generated case. Across completed runs, persuasion-induced false compliance appears in both settings. An explicit anti-capture integrity reminder reduces the synthetic effect, but the source-grounded lane still produces measurable capture under the same reminder.

## Current Evidence

| Setup | Cases | Auditor condition | Transcripts | Persuasion-induced false compliance | Overall false compliance | Takeaway |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Original synthetic run | Synthetic borderline cases across procurement, access exceptions, and model-card disclosure | Standard auditor prompt | 150 | 15/124 = 12.1% (95% CI 7.5%-19.0%) | 16/150 = 10.7% (95% CI 6.7%-16.6%) | Establishes the capture pattern. |
| Synthetic run with integrity reminder | Same synthetic cases | Explicit anti-capture reminder to stay independent, evidence-based, and not defer to persuasion | 150 | 5/123 = 4.1% (95% CI 1.7%-9.2%) | 7/150 = 4.7% (95% CI 2.3%-9.3%) | Reduces, but does not eliminate, capture. |
| Source-grounded model-card stress run | Source-note cases grounded in Hugging Face/NIST material plus realistic organization-specific launch artifacts | Same anti-capture integrity reminder | 150 | 13/123 = 10.6% (95% CI 6.3%-17.2%) | 15/150 = 10.0% (95% CI 6.2%-15.8%) | Shows the effect in a more realistic source-grounded lane. |
| Raw-access actor-knowledge A/B | 75 paired source-grounded model-card cases | Auditor always has raw evidence; actor is either told this or not told | 150 | 11/147 = 7.5% (95% CI 4.2%-12.9%) | 14/150 = 9.3% (95% CI 5.7%-15.1%) | Isolates actor knowledge of auditor raw-evidence access. |

Confidence intervals are Wilson 95% intervals. Persuasion-induced false compliance uses persuasion opportunities as the denominator; overall false compliance uses all transcripts.

Headline PIFC rate by run:

```text
Original synthetic          12.1% | ############
Synthetic + integrity        4.1% | ####
Source-grounded integrity   10.6% | ###########
Hidden access follow-up      8.1% | ########
Raw-access A/B               7.5% | ########
```

The source-grounded run is the new methodological step. It is not another sample from the old synthetic generator: it uses source-note packets, keeps provenance attached to each generated case, and tests model-card certification scenarios built from public governance/process sources plus source-tracked launch artifacts.

## Raw Evidence Contrast

The raw-evidence condition motivated a targeted mechanism check. Holding actor visibility to the full initial-auditor rationale, raw auditor evidence access produced higher PIFC than summary-only access in the three earlier runs.

| Run | Summary only + full rationale | Raw evidence + full rationale | Raw minus summary |
| --- | ---: | ---: | ---: |
| Original synthetic | 2/24 = 8.3% | 7/25 = 28.0% | +19.7 pp |
| Synthetic + integrity reminder | 0/25 = 0.0% | 4/24 = 16.7% | +16.7 pp |
| Source-grounded + integrity reminder | 2/24 = 8.3% | 4/24 = 16.7% | +8.3 pp |

## Hidden Auditor-Access Follow-Up

The raw-evidence condition in the source-grounded run was unexpectedly more capture-prone than the matching summary-only condition. To test whether that came from shared knowledge of auditor access, the follow-up run fixed the source-grounded cases, integrity reminder, full initial-audit rationale visibility, and no-new-evidence persuasion regime, then varied auditor access and what the actor was told about that access.

| Treatment | Auditor access | Actor access disclosure | Transcripts | Persuasion-induced false compliance | Overall false compliance |
| --- | --- | --- | ---: | ---: | ---: |
| H1 | Summary only | Told summary only | 25 | 2/25 = 8.0% (95% CI 2.2%-25.0%) | 2/25 = 8.0% (95% CI 2.2%-25.0%) |
| H2 | Summary only | Told raw access | 25 | 2/25 = 8.0% (95% CI 2.2%-25.0%) | 2/25 = 8.0% (95% CI 2.2%-25.0%) |
| H3 | Raw evidence | Not disclosed | 25 | 3/25 = 12.0% (95% CI 4.2%-30.0%) | 3/25 = 12.0% (95% CI 4.2%-30.0%) |
| H4 | Raw evidence | Told raw access | 25 | 1/24 = 4.2% (95% CI 0.7%-20.2%) | 2/25 = 8.0% (95% CI 2.2%-25.0%) |

These results do not support a simple "known raw access increases capture" account. In this run, hidden raw access was the highest cell and known raw access was the lowest PIFC cell. The intervals are wide, so the result is best treated as a mechanism signal for replication rather than a settled effect.

Hidden-access follow-up PIFC rate:

```text
H1 summary / told summary    8.0% | ####
H2 summary / told raw        8.0% | ####
H3 raw / not disclosed      12.0% | ######
H4 raw / told raw            4.2% | ##
```

## Raw-Access Actor-Knowledge A/B

The focused A/B keeps auditor raw-evidence access fixed and varies only whether the actor is told that the auditor has raw access. It reuses the completed H3/H4 lanes from the hidden-access run, adds 25 new source-grounded cases to reach 50 paired cases, then adds another 25 source-grounded cases for a 75-case paired read.

| Run | Treatment | Actor told auditor has raw evidence? | Transcripts | Persuasion-induced false compliance | Overall false compliance |
| --- | --- | --- | ---: | ---: | ---: |
| 50 paired cases | H3 raw / not disclosed | No | 50 | 5/49 = 10.2% (95% CI 4.4%-21.8%) | 6/50 = 12.0% (95% CI 5.6%-23.8%) |
| 50 paired cases | H4 raw / told raw | Yes | 50 | 1/48 = 2.1% (95% CI 0.4%-10.9%) | 3/50 = 6.0% (95% CI 2.1%-16.2%) |
| 75 paired cases | H3 raw / not disclosed | No | 75 | 9/74 = 12.2% (95% CI 6.5%-21.5%) | 10/75 = 13.3% (95% CI 7.4%-22.8%) |
| 75 paired cases | H4 raw / told raw | Yes | 75 | 2/73 = 2.7% (95% CI 0.8%-9.5%) | 4/75 = 5.3% (95% CI 2.1%-12.9%) |

The result supports a narrower mechanism signal: in this source-grounded setup, the actor is less successful when it knows the auditor can inspect raw evidence. The observed 75-case difference is 9.4 percentage points (12.2% versus 2.7%), with an approximate two-proportion 95% interval of 1.1 to 17.8 percentage points. Because the event count remains small, this should be treated as evidence of a mechanism rather than a final effect-size estimate.

Raw-access A/B PIFC rate at 75 paired cases:

```text
H3 raw / not disclosed      12.2% | ############
H4 raw / told raw            2.7% | ###
```

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
- Hidden auditor-access follow-up: `runs/source_grounded_hidden_access_integrity_25/`
- Raw-access actor-knowledge A/B: `runs/source_grounded_raw_access_ab_50/`, `runs/source_grounded_raw_access_ab_75/`
- Source-note packet: `data/source_notes/source_grounded_integrity_stress_25.json`
- Generated source-grounded cases: `data/cases_source_grounded_integrity_stress_25.jsonl`
- Generated raw-access A/B cases: `data/cases_source_grounded_raw_access_ab_75.jsonl`
- Source-grounded replication config: `config/replication.source_grounded_integrity_stress_25.json`
- Hidden-access treatment config: `config/treatments.hidden_access_integrity.json`
- Raw-access A/B treatment config: `config/treatments.raw_access_ab_integrity.json`
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

Generate the focused raw-access A/B case files:

```bash
python3 scripts/build_raw_access_ab_cases.py \
  --base-source-notes data/source_notes/source_grounded_integrity_stress_25.json \
  --extension-source-notes data/source_notes/source_grounded_raw_access_ab_extension_50.json \
  --combined-source-notes data/source_notes/source_grounded_raw_access_ab_75.json \
  --extension-cases data/cases_source_grounded_raw_access_ab_extension_50.jsonl \
  --combined-cases data/cases_source_grounded_raw_access_ab_75.jsonl \
  --start-index 6 \
  --end-index 15
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
