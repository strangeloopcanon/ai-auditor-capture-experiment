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

`data/source_notes/source_grounded_integrity_stress_25.json` is a deliberately model-card-heavy stress set for the integrity-reminder condition. It does not change the prompts, treatment config, scoring rules, or integrity reminder. The only change is the case material.

The cases are deliberately less tidy than a minimal fixture because the evidence is meant to look more like real launch residue:

- stale prior approval for an earlier release
- draft mitigation with missing owner or threshold
- unresolved materiality dispute
- missing eval coverage for named deployment contexts
- rollout or monitoring controls that do not actually exclude the weak segment

These are not meant to trick the scorer. In each case the Actor has plausible business-facing artifacts, but still lacks the specific admissible evidence needed for clean certification. In the completed run, the Auditor still moved to false compliance in 13 of 123 persuasion opportunities, which is the signal this lane is meant to stress-test.

The fixture has 25 cases: five variants of each near-miss artifact family. Running all six integrity-reminder conditions produces 150 transcripts, 125 persuasion opportunities, and a 550-call maximum budget.

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

Plan repeated integrity-stress runs without spending calls:

```bash
python3 scripts/run_replications.py \
  --config config/replication.source_grounded_integrity_stress_25.json \
  --repeats 5 \
  --plan-only
```

See `docs/replication_plan.md` for the exact 3-, 5-, and 10-repeat budgets and output folder layout.
