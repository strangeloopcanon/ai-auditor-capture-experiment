# Self-Generated Concern Ledger

This is the realistic concern-accounting rerun.

The earlier mitigation handed the final auditor the initial auditor's `specific_concerns` and required explicit accounting. That is the clean mechanism test: a complete checklist plus a strict closure rule. This run asks a harder question: can the auditor create its own formal ledger at the initial stage, keep it private from the actor, and use it at final review?

The answer is mixed in the useful way. Self-generated ledgers sharply reduce PIFC. They also expose the next failure surface: the auditor can maintain the ledger loosely, omit pressure points, or close rows without new admissible evidence.

## Design

The run starts from `runs/source_grounded_raw_access_ab_fixed_150/`, treatment `H3_raw_hidden_access_integrity`.

The actor decision is reused. That stage happens before any audit or ledger exists. Every later stage is rerun because the initial auditor's prompt changes:

1. The initial auditor creates a private `concern_ledger`.
2. The actor receives the ordinary public initial audit, with `concern_ledger` stripped.
3. The final auditor is tested in paired arms over the same actor response.

| Arm | Actor response | Final-auditor state |
| --- | --- | --- |
| `SL0_self_ledger_standard_final` | Ordinary actor response | Full public initial audit, no private ledger |
| `SL1_self_ledger_final` | Ordinary actor response | Full public initial audit plus the private ledger, which must be updated |
| `SL2_self_ledger_stress_standard_final` | Longer state-tracking-stress response | Full public initial audit, no private ledger |
| `SL3_self_ledger_stress_final` | Longer state-tracking-stress response | Full public initial audit plus the private ledger, which must be updated |

The 50-case pilot uses the same high-concern selection as the state-tracking stress run. The full result uses all 150 fixed-boundary source-grounded cases.

## Results

| Run | Arm | PIFC | Overall false compliance | Ledger note |
| --- | --- | ---: | ---: | --- |
| 50-case pilot | Standard final | 4/50 = 8.0% | 4/50 = 8.0% | Ledger created but not available at final review |
| 50-case pilot | Ledger final | 0/50 = 0.0% | 0/50 = 0.0% | Unsupported ledger closure in 10/50 cases |
| Full 150 | Standard final | 8/149 = 5.4% | 9/150 = 6.0% | Ledger created but not available at final review |
| Full 150 | Ledger final | 2/149 = 1.3% | 3/150 = 2.0% | Unsupported ledger closure in 34/149 continued cases |
| 50-case stress pilot | Standard final | 0/50 = 0.0% | 0/50 = 0.0% | No observed PIFC in either arm |
| 50-case stress pilot | Ledger final | 0/50 = 0.0% | 0/50 = 0.0% | Unsupported ledger closure in 11/50 cases |
| Full 150 stress | Standard final | 3/148 = 2.0% | 5/150 = 3.3% | Ledger created but not available at final review |
| Full 150 stress | Ledger final | 0/148 = 0.0% | 2/150 = 1.3% | Unsupported ledger closure in 52/148 continued cases |

## Place in the ladder

| Mitigation step | Who supplies the state? | Final-auditor task | Result |
| --- | --- | --- | ---: |
| Exact concern accounting | The experiment supplies the complete initial concern checklist | Check each item against new admissible evidence | 0/143 PIFC |
| Exact accounting under stress | The experiment supplies the complete checklist after a messier actor response | Preserve each unresolved item | 0/50 PIFC |
| Self-generated ledger | The auditor creates the ledger itself | Update its own private ledger before deciding | 2/149 PIFC |
| Self-generated ledger under stress | The auditor creates the ledger itself and receives it after a longer actor response | Update the ledger under state-tracking pressure | 0/148 PIFC |

This is the important distinction. When the final auditor is handed a complete checklist and no new evidence appears, it works in the observed fixed-boundary run. When the auditor has to create and maintain the same discipline itself, the mitigation still helps but becomes imperfect.

## Reading

Self-generated ledgers help, with residual failures.

In the ordinary full run, giving the final auditor the private ledger reduced PIFC from 8/149 to 2/149. Those two remaining cases are ledger escapes: the final auditor had a ledger and still reached false compliance without new admissible evidence.

Under state-tracking stress, the ledger-final arm had no observed PIFC in 148 persuasion opportunities. That is encouraging, especially because the actor response was longer and harder to track. The standard final arm still had 3/148 PIFC cases.

The main limit is procedural. Ledger-final auditors sometimes marked a concern closed or partly closed without genuinely new admissible evidence: 34/149 in the ordinary full run and 52/148 in the stress full run. Most of those did not become PIFC, but they show the ledger itself can be handled too loosely.

The best conclusion is:

> Concern accounting is a strong mitigation because the failure is mechanistic. It works by keeping unresolved concerns alive. But a self-generated ledger is only as good as the auditor's bookkeeping: the auditor can still omit a concern, soften a concern, or close a row without new evidence.

## Artifacts

- `runs/source_grounded_self_ledger_50/`
- `runs/source_grounded_self_ledger_50_comparison/`
- `runs/source_grounded_self_ledger_stress_50/`
- `runs/source_grounded_self_ledger_stress_50_comparison/`
- `runs/source_grounded_self_ledger_150/`
- `runs/source_grounded_self_ledger_150_comparison/`
- `runs/source_grounded_self_ledger_stress_150/`
- `runs/source_grounded_self_ledger_stress_150_comparison/`

## Reproduce

Run the ordinary full self-ledger rerun:

```bash
python3 scripts/rerun_self_ledger_workflow.py \
  --cases data/cases_source_grounded_raw_access_ab_150.jsonl \
  --treatments config/treatments.self_ledger_integrity.json \
  --manifest config/run_manifest.mvp.json \
  --source-run runs/source_grounded_raw_access_ab_fixed_150 \
  --source-treatment H3_raw_hidden_access_integrity \
  --out runs/source_grounded_self_ledger_150 \
  --execute
```

Run the full state-tracking-stress self-ledger rerun:

```bash
python3 scripts/rerun_self_ledger_workflow.py \
  --cases data/cases_source_grounded_raw_access_ab_150.jsonl \
  --treatments config/treatments.self_ledger_stress_integrity.json \
  --manifest config/run_manifest.mvp.json \
  --source-run runs/source_grounded_raw_access_ab_fixed_150 \
  --source-treatment H3_raw_hidden_access_integrity \
  --out runs/source_grounded_self_ledger_stress_150 \
  --execute
```

Large runs can also be split into chunks and recombined with `scripts/combine_run_chunks.py`.
