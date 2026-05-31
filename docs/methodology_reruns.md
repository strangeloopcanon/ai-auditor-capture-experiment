# Methodology Reruns

These reruns clean up three methodology questions:

1. Compare source-grounded cases with and without the auditor integrity reminder.
2. Rerun the original raw-vs-summary cases through the fixed actor-visible treatment boundary.
3. Rerun the raw-access actor-knowledge A/B through the same fixed boundary.

The fixed boundary hides auditor-only treatment fields from the actor-decision prompt. The actor-decision prompt now omits fields such as `evidence_access`, `actor_auditor_access_disclosure`, `auditor_integrity_reminder`, and `selective_continuation`. Response-stage access disclosure is still shown when the treatment is meant to test it.

## Runs

The important denominator distinction is:

- `Base cases`: unique scenario fixtures.
- `Transcripts`: base cases expanded across treatment arms.
- `PIFC denominator`: continued persuasion opportunities, after no-response and skipped selective-continuation transcripts are excluded.

| Question | Base cases | Treatment arms | Transcripts | PIFC denominator | Output |
| --- | ---: | ---: | ---: | ---: | --- |
| Source-grounded stress, no reminder | 25 | 6 | 150 | 121 | `runs/source_grounded_stress_no_integrity_fixed_25/` |
| Source-grounded stress, integrity reminder | 25 | 6 | 150 | 124 | `runs/source_grounded_stress_integrity_fixed_25/` |
| Raw-vs-summary on original cases, fixed boundary | 150 | 2 | 300 | raw 144; summary 150 | `runs/source_grounded_raw_vs_summary_original_cases_fixed_150/` |
| Raw-access actor knowledge, fixed boundary | 150 | 2 | 300 | not told 143; told 145 | `runs/source_grounded_raw_access_ab_fixed_150/` |

## Results

| Check | Arm | PIFC | Overall false compliance |
| --- | --- | ---: | ---: |
| Source-grounded stress | No integrity reminder | 21/121 = 17.4% (95% CI 11.6%-25.1%) | 25/150 = 16.7% (95% CI 11.6%-23.4%) |
| Source-grounded stress | Integrity reminder | 7/124 = 5.6% (95% CI 2.8%-11.2%) | 8/150 = 5.3% (95% CI 2.7%-10.2%) |
| Raw-vs-summary, original cases, fixed boundary | Raw evidence | 11/144 = 7.6% (95% CI 4.3%-13.2%) | 17/150 = 11.3% (95% CI 7.2%-17.4%) |
| Raw-vs-summary, original cases, fixed boundary | Summary only | 5/150 = 3.3% (95% CI 1.4%-7.6%) | 5/150 = 3.3% (95% CI 1.4%-7.6%) |
| Raw-access actor knowledge, fixed boundary | Actor not told | 6/143 = 4.2% (95% CI 1.9%-8.9%) | 13/150 = 8.7% (95% CI 5.1%-14.3%) |
| Raw-access actor knowledge, fixed boundary | Actor told | 14/145 = 9.7% (95% CI 5.8%-15.6%) | 19/150 = 12.7% (95% CI 8.3%-18.9%) |

## Follow-On Mitigation Ladder

The concern-accounting final-auditor intervention was repeated on the fixed-boundary raw-access interaction set. It reuses the `H3_raw_hidden_access_integrity` actor-decision, initial-audit, and actor-response stages from `runs/source_grounded_raw_access_ab_fixed_150/`, then reruns only the final auditor with the unresolved-concern accounting instruction.

| Arm | PIFC | Overall false compliance |
| --- | ---: | ---: |
| Standard final audit | 6/143 = 4.2% (95% CI 1.9%-8.9%) | 13/150 = 8.7% (95% CI 5.1%-14.3%) |
| Concern accounting final audit | 0/143 = 0.0% (95% CI 0.0%-2.6%) | 7/150 = 4.7% (95% CI 2.3%-9.3%) |

Paired PIFC discordance: 6 standard-only failures, 0 accounting-only failures, exact McNemar p = 0.03125.

The later ledger runs extend this mitigation in two steps. First, the exact concern checklist is kept available under state-tracking stress. Then the auditor must create and maintain its own private `concern_ledger`.

| Mitigation step | PIFC | Reading |
| --- | ---: | --- |
| Exact concern accounting | 0/143 | A complete supplied checklist blocked observed PIFC on the fixed-boundary interaction set. |
| Exact concern accounting under stress | 0/50 | The supplied checklist survived a longer, messier actor response in the pilot. |
| Compressed handoff under stress | 1/50 | Losing the exact checklist reintroduced one observed failure. |
| Self-generated ledger, full fixed-boundary set | 2/149 | Auditor-created bookkeeping sharply reduced PIFC but left ledger escapes. |
| Self-generated ledger, full stress set | 0/148 | No observed PIFC remained under stress, while unsupported ledger closure stayed high. |

Canonical artifacts:

- `runs/source_grounded_raw_accounting_fixed_150/`
- `runs/source_grounded_raw_accounting_fixed_150_comparison/`
- `runs/source_grounded_state_tracking_stress_accounting_50/`
- `runs/source_grounded_state_tracking_stress_handoff_50/`
- `runs/source_grounded_self_ledger_150/`
- `runs/source_grounded_self_ledger_150_comparison/`
- `runs/source_grounded_self_ledger_stress_150/`
- `runs/source_grounded_self_ledger_stress_150_comparison/`

## Reading

The source-grounded reminder comparison is now clean: the same 25 model-card cases were run with and without the integrity reminder. The reminder reduces PIFC from 17.4% to 5.6%.

The raw-vs-summary result is narrower. On the original cases, the fixed-boundary rerun still has higher raw-arm PIFC than summary-arm PIFC, but the paired PIFC contrast is uncertain. The fresh fixed-boundary replication lands near parity.

The actor-knowledge result changed direction under the fixed boundary. The old run had lower PIFC when the actor was told the auditor had raw access. The fixed-boundary rerun has higher PIFC in the told arm, but the contrast is still uncertain.

The concern-accounting mitigation remains the strongest intervention. In the fixed-boundary rerun it removed all observed PIFC, while overall false compliance remained at 7/150. The self-generated ledger runs make the same idea more realistic: the auditor creates the state itself, and the final auditor uses it later. That version reduces PIFC from 8/149 to 2/149 on the full fixed-boundary set and from 3/148 to 0/148 under stress. The remaining issue is ledger discipline, especially closing rows without genuinely new admissible evidence.

All current source-grounded fixtures are model-card disclosure cases. Realistic source-grounded domain effects require new source-note packets.

## Commands

Plan all reruns without spending calls:

```bash
python3 scripts/run_methodology_reruns.py --which all --plan-only
```

Run them with case chunks:

```bash
python3 scripts/run_methodology_reruns.py \
  --which all \
  --execute \
  --parallel-chunks \
  --jobs 5 \
  --overwrite
```

Run one group:

```bash
python3 scripts/run_methodology_reruns.py \
  --which phase3 \
  --execute \
  --parallel-chunks \
  --jobs 5 \
  --overwrite
```

Use `--summary-out <path>` when a persistent invocation summary is needed.
