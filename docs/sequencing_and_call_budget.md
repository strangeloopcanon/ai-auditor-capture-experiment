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

## Next Sequencing

The next useful extensions are:

1. Focused replication of the 150-case balanced run to estimate run-to-run variance.
2. Model-family comparison, such as `gpt-5.5` Actor against `gpt-5.4` Auditor.
3. Full Cartesian design only if treatment-level causal estimates become necessary.

Do not run the full Cartesian design by default. The current publishable claim does not require 3,300 calls.
