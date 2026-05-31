# Replication Plan

This plan repeats the completed 25-case source-grounded integrity stress test. It is meant to estimate stability of the observed signal, not to introduce a new benchmark.

## Frozen Setup

- Cases: `data/cases_source_grounded_integrity_stress_25.jsonl`
- Treatments: `config/treatments.integrity_reminder.json`
- Manifest: `config/run_manifest.mvp.json`
- Models: `gpt-5.4` Actor and `gpt-5.4` Auditor through Codex
- Assignment: `all_conditions`
- Output root: `runs/replications/source_grounded_integrity_stress_25_integrity/`

The repeat runner does not change prompts, scoring, treatments, source notes, or model family. Each repeat gets a distinct assignment seed and a distinct output folder:

```text
runs/replications/source_grounded_integrity_stress_25_integrity/
  repeat_001_seed_2026051601/
  repeat_002_seed_2026051602/
  repeat_003_seed_2026051603/
```

For `all_conditions`, the seed only changes execution order, because every case is run under every treatment. The seed is still recorded so repeated runs have explicit provenance and can be reproduced exactly.

## Exact Budgets

Per repeat:

```text
25 base cases x 6 integrity conditions = 150 transcripts
1 no-response condition x 25 cases x 2 calls = 50 calls
5 response conditions x 25 cases x 4 calls = 500 calls
Maximum per repeat = 550 Codex calls
```

The response-condition count is a call budget, not necessarily the PIFC denominator. PIFC uses continued persuasion opportunities, so selective continuation can reduce the denominator below the maximum 125 response-condition slots.

Repeated budgets:

```text
3 repeats  = 450 transcripts, 1,650 max calls
5 repeats  = 750 transcripts, 2,750 max calls
10 repeats = 1,500 transcripts, 5,500 max calls
```

Actual call counts may be slightly lower if a selective continuation is skipped after an initial compliant-with-caveats verdict. The budget above is the exact maximum before execution.

## Commands

Plan without spending calls:

```bash
python3 scripts/run_replications.py \
  --config config/replication.source_grounded_integrity_stress_25.json \
  --repeats 5 \
  --plan-only
```

Execute five repeats:

```bash
python3 scripts/run_replications.py \
  --config config/replication.source_grounded_integrity_stress_25.json \
  --repeats 5 \
  --execute
```

The runner writes `replication_plan.json`, one `run_metadata.json` per repeat, the standard run artifacts for each repeat, and a top-level `replication_summary.json`.
