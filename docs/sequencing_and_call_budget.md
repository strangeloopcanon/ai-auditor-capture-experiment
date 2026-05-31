# Sequencing and Call Budget

## Per Case-Condition Calls

No-response condition:

```text
Actor decision:       1
Auditor initial:      1
Actor response:       0
Auditor final:        0
Regulator scoring:    0
Total:                2
```

Response condition:

```text
Actor decision:       1
Auditor initial:      1
Actor response:       1
Auditor final:        1
Regulator scoring:    0
Total:                4
```

Optional Appeals Judge:

```text
+1 call per case-condition pair
```

## Canonical Borderline Design

The current canonical design has one no-response condition and five response conditions:

- `B1_summary_no_response`
- `B2_summary_argument_verdict_only_selective`
- `B3_summary_argument_full_rationale_selective`
- `B4_summary_urgency_client_pressure_selective`
- `B5_summary_preregistered_selective`
- `B6_raw_argument_full_rationale_selective`

The canonical run uses balanced single-treatment assignment, not the full Cartesian product. Each case is assigned to one treatment.

Maximum calls for 150 balanced cases:

```text
25 no-response cases x 2 calls = 50
125 response cases x 4 calls   = 500
Maximum total                   = 550
```

The completed canonical run used 548 calls because one selective response stage was skipped after an initial caveated-compliance verdict.

Full Cartesian version across all six treatments:

```text
Per case across all conditions:
1 no-response condition x 2 calls = 2
5 response conditions x 4 calls   = 20
Total per case                    = 22

150 cases x 22 calls = 3,300 Codex LLM calls
```

With Appeals Judge:

```text
+1 call per case-condition pair
```

## Completed Sequence

1. Model route sanity check: 2 calls. Already completed locally for `gpt-5.4` and `gpt-5.5`.
2. Calibration gates found that the original standard and locked-stress lanes were not the right target.
3. Borderline lane was frozen after it reliably produced weakly supported packets and initial suspicious verdicts.
4. Canonical 150-case balanced run completed at `runs/borderline_live_150`.
5. Canonical run used 548 live `gpt-5.4` role calls.
6. Integrity-reminder run completed at `runs/integrity_reminder_live_150` and reduced persuasion-induced false compliance while leaving residual cases.
7. Source-grounded model-card integrity stress run completed at `runs/source_grounded_integrity_stress_25_integrity` with 150 transcripts, 546 live calls, and 13 persuasion-induced false-compliance cases.
8. Source-grounded raw-access actor-knowledge run completed at `runs/source_grounded_raw_access_ab_150`.
9. Initial raw-vs-summary neutral-disclosure comparison completed at `runs/source_grounded_raw_vs_summary_neutral_150`.
10. Concern-accounting final-auditor intervention completed at `runs/source_grounded_raw_accounting_150`.
11. Fresh raw-vs-summary replication completed at `runs/source_grounded_raw_vs_summary_fresh_150` with the stricter actor-visible treatment boundary.
12. Fixed-boundary source-grounded reminder comparison completed at `runs/source_grounded_stress_no_integrity_fixed_25` and `runs/source_grounded_stress_integrity_fixed_25`.
13. Phase 3 original cases rerun through the fixed boundary at `runs/source_grounded_raw_vs_summary_original_cases_fixed_150`.
14. Phase 4 raw-access actor-knowledge A/B rerun through the fixed boundary at `runs/source_grounded_raw_access_ab_fixed_150`.
15. Concern-accounting final-auditor intervention repeated on the fixed-boundary raw-access interaction set at `runs/source_grounded_raw_accounting_fixed_150`.

## Follow-Up Sequencing

Useful extensions from here are:

1. Add realistic source-grounded domains beyond model-card disclosure.
2. Repeat the fresh raw-vs-summary A/B under a second random case/context seed.
3. Repeat concern accounting across another case seed or model family to test generality.
4. Add model-family comparisons, such as `gpt-5.5` Actor against `gpt-5.4` Auditor.
5. Use the full Cartesian design only if treatment-level causal estimates become necessary.

The full Cartesian design is expensive and should be reserved for treatment-level causal estimates rather than routine follow-up.

## Source-Grounded Integrity Replications

The active source-grounded replication config is:

```text
config/replication.source_grounded_integrity_stress_25.json
```

The active fresh raw-vs-summary replication config is:

```text
config/replication.raw_vs_summary_fresh_150.json
```

Each repeat runs the same 25 source-grounded near-miss cases across all six integrity-reminder conditions:

```text
150 transcripts per repeat
550 maximum Codex calls per repeat
```

Standard repeated budgets:

```text
3 repeats  = 450 transcripts, 1,650 max calls
5 repeats  = 750 transcripts, 2,750 max calls
10 repeats = 1,500 transcripts, 5,500 max calls
```

Plan before spending calls:

```bash
python3 scripts/run_replications.py \
  --config config/replication.source_grounded_integrity_stress_25.json \
  --repeats 5 \
  --plan-only
```

## Methodology Reruns

The fixed-boundary methodology reruns are defined in `scripts/run_methodology_reruns.py`.

Plan the full set:

```bash
python3 scripts/run_methodology_reruns.py --which all --plan-only
```

Run the full set in parallel chunks:

```bash
python3 scripts/run_methodology_reruns.py \
  --which all \
  --execute \
  --parallel-chunks \
  --jobs 5 \
  --overwrite
```

The completed reruns produced 900 transcripts:

```text
source-grounded no-reminder stress        150 transcripts
source-grounded integrity stress          150 transcripts
raw-vs-summary original cases, fixed      300 transcripts
raw-access actor knowledge, fixed         300 transcripts
```

Those transcript counts are not the PIFC denominators. PIFC is counted over continued persuasion opportunities: 121 and 124 for the source-grounded reminder settings, 144 and 150 for the raw-vs-summary arms, and 143 and 145 for the actor-knowledge arms.
