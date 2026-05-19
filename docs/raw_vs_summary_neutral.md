# Raw-vs-Summary Neutral-Disclosure A/B

This study tests the direct raw-vs-summary access contrast:

> Holding actor access disclosure fixed, what happens when the auditor sees raw evidence instead of only the actor's summary?

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

The result is straightforward: the raw-evidence auditor produced more false compliance than the summary-only auditor. More evidence did not act as a simple safeguard in this setup.

The separate raw-access actor-knowledge A/B tests a narrower explanation: whether the actor needs to know about raw auditor access for the effect to appear. Actor awareness is not required in these runs, and disclosure moves the raw-access result lower.
