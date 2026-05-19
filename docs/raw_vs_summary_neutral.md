# Raw-vs-Summary Neutral-Disclosure A/B

This follow-up tests the direct raw-vs-summary question:

> Holding actor access disclosure fixed, does auditor raw-evidence access reduce or increase persuasion-induced false compliance relative to summary-only auditor access?

The design uses the same 150 source-grounded model-card cases in both arms. The actor receives the full initial-audit rationale in both arms, the persuasion regime is no-new-evidence argumentation in both arms, and the auditor receives the same anti-capture integrity reminder in both arms. The intended difference is auditor evidence access.

| Arm | Auditor access | Actor access disclosure |
|---|---|---|
| `RVS1_summary_not_disclosed_integrity` | Summary only | Not disclosed |
| `H3_raw_hidden_access_integrity` | Raw evidence | Not disclosed |

The summary-neutral arm is stored in `runs/source_grounded_summary_neutral_150/`. The raw-neutral arm is the H3 lane from `runs/source_grounded_raw_access_ab_150/`. The combined comparison artifact is stored in `runs/source_grounded_raw_vs_summary_neutral_150/`.

## Results

| Arm | PIFC | Overall false compliance |
|---|---:|---:|
| Summary neutral | 4/150 = 2.7% (95% CI 1.0%-6.7%) | 4/150 = 2.7% (95% CI 1.0%-6.7%) |
| Raw neutral | 16/145 = 11.0% (95% CI 6.9%-17.2%) | 21/150 = 14.0% (95% CI 9.3%-20.5%) |

Raw-evidence access is associated with higher PIFC in this setup: +8.4 percentage points relative to summary-only access, with an approximate independent two-proportion interval of +2.7 to +14.1 percentage points.

The paired case comparison points in the same direction:

| Metric | Raw only | Summary only | Both | Neither | Exact McNemar p |
|---|---:|---:|---:|---:|---:|
| PIFC | 14 | 2 | 2 | 132 | 0.00418 |
| Overall false compliance | 18 | 1 | 3 | 128 | 0.000076 |

## Interpretation

The result supports the counterintuitive raw-evidence vulnerability observed in earlier runs. In this design, raw evidence did not simply make the auditor stricter. With full rationale visibility and no-new-evidence persuasion, raw-evidence access produced more false compliance than summary-only access.

The separate raw-access actor-knowledge A/B tests a different mechanism: whether telling the actor about raw auditor access changes the outcome when the auditor has raw access in both arms. That result is directional but not conclusive, and it does not explain away the raw-vs-summary effect.
