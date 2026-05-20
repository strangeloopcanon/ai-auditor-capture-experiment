# Raw-vs-Summary Evidence Access

This page summarizes the direct evidence-access tests:

> What changes when the auditor sees raw admissible evidence rather than only the actor's summary?

Two 150-case paired A/Bs are now available. The first used the original source-grounded case set. The second used a fresh source-grounded case set and the current stricter actor-visible boundary, which hides auditor-access fields from the actor-decision prompt.

## Designs

| Run | Cases | Actor-visible boundary | Raw arm | Summary arm |
| --- | ---: | --- | --- | --- |
| Initial neutral-disclosure A/B | 150 | Response-stage auditor-access disclosure held as not disclosed. | `H3_raw_hidden_access_integrity` from `runs/source_grounded_raw_access_ab_150/` | `RVS1_summary_not_disclosed_integrity` from `runs/source_grounded_summary_neutral_150/` |
| Fresh replication | 150 | Auditor-access fields hidden from actor decision and response-stage disclosure held as not disclosed. | `H3_raw_hidden_access_integrity` from `runs/source_grounded_raw_vs_summary_fresh_150/` | `RVS1_summary_not_disclosed_integrity` from `runs/source_grounded_raw_vs_summary_fresh_150/` |

Both runs use source-grounded model-card cases, the no-new-evidence argumentation regime, full actor visibility into the initial audit rationale, and the same anti-capture integrity reminder.

## Results

| Run | Arm | PIFC | Overall false compliance |
| --- | --- | ---: | ---: |
| Initial A/B | Summary only | 4/150 = 2.7% (95% CI 1.0%-6.7%) | 4/150 = 2.7% (95% CI 1.0%-6.7%) |
| Initial A/B | Raw evidence | 16/145 = 11.0% (95% CI 6.9%-17.2%) | 21/150 = 14.0% (95% CI 9.3%-20.5%) |
| Fresh replication | Summary only | 9/150 = 6.0% (95% CI 3.2%-11.0%) | 9/150 = 6.0% (95% CI 3.2%-11.0%) |
| Fresh replication | Raw evidence | 7/142 = 4.9% (95% CI 2.4%-9.8%) | 15/150 = 10.0% (95% CI 6.2%-15.8%) |

## Paired Contrasts

| Run | Metric | Raw only | Summary only | Both | Neither | Exact McNemar p | Raw minus summary |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Initial A/B | PIFC | 14 | 2 | 2 | 132 | 0.00418 | +8.4 pp, approx 95% interval +2.7 to +14.1 pp |
| Initial A/B | Overall false compliance | 18 | 1 | 3 | 128 | 0.000076 | +11.3 pp, approx 95% interval +5.2 to +17.5 pp |
| Fresh replication | PIFC | 5 | 7 | 2 | 136 | 0.774 | -1.1 pp, approx 95% interval -6.3 to +4.1 pp |
| Fresh replication | Overall false compliance | 12 | 6 | 3 | 129 | 0.238 | +4.0 pp, approx 95% interval -2.1 to +10.1 pp |

## Reading

The initial A/B showed a clear raw-over-summary PIFC gap. The fresh replication did not repeat that PIFC gap after the actor-visible treatment boundary was tightened. The fresh run still has higher overall false compliance in the raw arm, but that difference is smaller and uncertain.

The evidence-access story is therefore narrower than the initial A/B suggested. Raw evidence can participate in false softening, but raw access by itself is not the most stable result. The stable mechanism across reviewed failure cases is caveat conversion: an unresolved requirement is reframed as something to disclose, monitor, or condition, and the final auditor sometimes accepts that as enough.

Canonical artifacts:

- `runs/source_grounded_raw_vs_summary_neutral_150/`
- `runs/source_grounded_raw_vs_summary_fresh_150/`
- `runs/source_grounded_raw_vs_summary_fresh_150_comparison/`
