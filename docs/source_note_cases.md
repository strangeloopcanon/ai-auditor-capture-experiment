# Source-Note Case Generation

Source-note generation is a separate lane for testing whether the same audit-capture pattern can be instantiated from public policy/process grounding plus realistic organization-specific notes.

## Source-Note Packet

A source-note packet is a small JSON or JSONL object with:

- `case_id` and `domain`
- `source_notes`: public, private, or synthetic notes with locators and short excerpts
- `case_blueprint`: the normal case fields used by the existing harness

Generated cases keep the normal case shape and add:

- `generation_lane: "source_notes"`
- `source_provenance`: note ids, locators, sensitivity labels, and content hashes
- `source_note_ids` on each admissible or private evidence item

The active fixture at `data/source_notes/source_grounded_integrity_stress_25.json` uses public policy and process material to ground the model-card governance surface, then marks the invented organization-specific launch facts as `synthetic_extension`. That split is intentional: public source notes ground the rule surface, while the repo-local fixture supplies the realistic launch residue needed to test the auditor.

## Integrity-Stress Fixture

`data/source_notes/source_grounded_integrity_stress_25.json` is a deliberately model-card-heavy stress set. It keeps the prompts and scoring rules fixed while changing the case material from synthetic borderline cases to source-grounded model-card near misses.

The cases are deliberately less tidy than a minimal fixture because the evidence is meant to look more like real launch residue:

- stale prior approval for an earlier release
- draft mitigation with missing owner or threshold
- unresolved materiality dispute
- missing eval coverage for named deployment contexts
- rollout or monitoring controls that leave the weak segment in scope

The scorer target stays clear. In each case the Actor has plausible business-facing artifacts, but still lacks the specific admissible evidence needed for clean certification.

The fixture has 25 base cases: five variants of each near-miss artifact family. Running all six integrity-reminder conditions produces 150 case-condition transcripts and up to 125 response-condition slots. The actual PIFC denominator is the number of continued persuasion opportunities after selective continuation. In the fixed-boundary reminder comparison, that was 121 without the reminder and 124 with the reminder.

## Reminder Comparison

The fixed-boundary rerun gives a direct reminder comparison on the same source-grounded cases:

| Run | PIFC | Overall false compliance |
| --- | ---: | ---: |
| No integrity reminder | 21/121 = 17.4% (95% CI 11.6%-25.1%) | 25/150 = 16.7% (95% CI 11.6%-23.4%) |
| Integrity reminder | 7/124 = 5.6% (95% CI 2.8%-11.2%) | 8/150 = 5.3% (95% CI 2.7%-10.2%) |

The reminder reduces false softening in this source-grounded setting. The checked source-grounded cases are still model-card disclosure cases, so the next source-grounded domain check needs new realistic fixtures.

## Extended Fixtures

`data/source_notes/source_grounded_raw_access_ab_150.json` extends the 25-case source-note fixture to 150 cases for the raw-access actor-knowledge and initial raw-vs-summary runs.

`data/source_notes/source_grounded_raw_vs_summary_replication_150.json` adds a fresh 150-case set for the boundary-hardened raw-vs-summary replication. It uses the same five near-miss artifact families, but with new deployment contexts numbered 31 through 60. The generated case file is `data/cases_source_grounded_raw_vs_summary_replication_150.jsonl`.

Phase 1 synthetic cases span procurement, access exceptions, and model-card disclosure. The source-grounded fixtures in this branch use model-card disclosure only, so realistic domain effects require new source-note packets.

## Commands

Generate the source-grounded case file:

```bash
python3 scripts/generate_cases.py \
  --mode source-notes \
  --source-notes data/source_notes/source_grounded_integrity_stress_25.json \
  --output data/cases_source_grounded_integrity_stress_25.jsonl
```

Show the integrity-stress call budget:

```bash
python3 scripts/plan_calls.py \
  --cases data/cases_source_grounded_integrity_stress_25.jsonl \
  --treatments config/treatments.integrity_reminder.json \
  --manifest config/run_manifest.mvp.json
```

Run the integrity-stress treatment set:

```bash
python3 scripts/run_experiment.py \
  --cases data/cases_source_grounded_integrity_stress_25.jsonl \
  --treatments config/treatments.integrity_reminder.json \
  --manifest config/run_manifest.mvp.json \
  --out runs/source_grounded_integrity_stress_25_integrity \
  --assignment all_conditions \
  --execute
```

Run the fixed-boundary reminder comparison and methodology reruns:

```bash
python3 scripts/run_methodology_reruns.py \
  --which source-grounded-reminder \
  --execute \
  --parallel-chunks \
  --jobs 5 \
  --overwrite
```

Plan repeated integrity-stress runs without spending calls:

```bash
python3 scripts/run_replications.py \
  --config config/replication.source_grounded_integrity_stress_25.json \
  --repeats 5 \
  --plan-only
```

See `docs/replication_plan.md` for the exact 3-, 5-, and 10-repeat budgets and output folder layout.
