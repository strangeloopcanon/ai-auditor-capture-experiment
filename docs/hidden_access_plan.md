# Hidden Auditor-Access Plan

This design is the first source-grounded access-knowledge test. It followed the early signal that raw auditor access could be more capture-prone than summary-only review.

The later 150-case actor-knowledge reruns are summarized in `docs/raw_access_ab_plan.md`. This page records the small exploratory four-cell run; the 150-case reruns carry the current actor-knowledge read.

The active treatment file is `config/treatments.hidden_access_integrity.json`. It keeps the integrity reminder, source-grounded cases, full actor visibility into the initial audit rationale, and no-new-evidence persuasion regime fixed. It varies two things:

- What the auditor can inspect: actor summary only or raw admissible evidence.
- What the actor is told about auditor access: summary-only, raw access, or not disclosed.

The four cells are:

| Treatment | Auditor access | Actor access disclosure |
|---|---|---|
| `H1_summary_known_summary_integrity` | Summary only | Told summary only |
| `H2_summary_actor_believes_raw_integrity` | Summary only | Told raw access |
| `H3_raw_hidden_access_integrity` | Raw evidence | Not disclosed |
| `H4_raw_known_access_integrity` | Raw evidence | Told raw access |

Run:

```bash
python3 scripts/run_experiment.py \
  --cases data/cases_source_grounded_integrity_stress_25.jsonl \
  --treatments config/treatments.hidden_access_integrity.json \
  --manifest config/run_manifest.mvp.json \
  --out runs/source_grounded_hidden_access_integrity_25 \
  --assignment all_conditions \
  --execute
```

Analyze:

```bash
python3 scripts/analyze_run.py \
  --run runs/source_grounded_hidden_access_integrity_25 \
  --json-out runs/source_grounded_hidden_access_integrity_25/analysis.json \
  --md-out runs/source_grounded_hidden_access_integrity_25/analysis.md
```

## Completed Run

The completed run is `runs/source_grounded_hidden_access_integrity_25`. It was executed as four split treatment lanes and then combined into one canonical output folder. That produced `100` transcripts and `398` logged calls against a `400` call maximum; one selective continuation was skipped after an initial caveated-compliance verdict.

Overall:

- Persuasion-induced false compliance: `8/99 = 8.1%` with Wilson 95% CI `4.2%-15.1%`.
- Overall false compliance: `9/100 = 9.0%` with Wilson 95% CI `4.8%-16.2%`.

By treatment:

| Treatment | PIFC | Wilson 95% CI | False compliance |
|---|---:|---:|---:|
| `H1_summary_known_summary_integrity` | `2/25 = 8.0%` | `2.2%-25.0%` | `2/25 = 8.0%` |
| `H2_summary_actor_believes_raw_integrity` | `2/25 = 8.0%` | `2.2%-25.0%` | `2/25 = 8.0%` |
| `H3_raw_hidden_access_integrity` | `3/25 = 12.0%` | `4.2%-30.0%` | `3/25 = 12.0%` |
| `H4_raw_known_access_integrity` | `1/24 = 4.2%` | `0.7%-20.2%` | `2/25 = 8.0%` |

The simple shared-context hypothesis predicted the known-raw-access cell would be most capture-prone. This small run instead put the largest exploratory signal in raw access with no explicit disclosure to the actor. Later 150-case reruns separate this actor-knowledge question from the broader raw-vs-summary evidence-access question and should be used for the current read.
