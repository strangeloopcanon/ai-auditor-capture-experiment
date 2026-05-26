# Raw-vs-Summary Evidence Access

This page summarizes the direct evidence-access tests:

> What changes when the auditor sees raw admissible evidence rather than only the actor's summary?

Three 150-case paired A/Bs are available. The initial run showed a raw-over-summary PIFC gap. The original-case fixed-boundary rerun narrows that gap. The fresh fixed-boundary replication lands near parity.

## Designs

| Run | Cases | Actor-visible boundary | Raw arm | Summary arm |
| --- | ---: | --- | --- | --- |
| Initial neutral-disclosure A/B | 150 | Response-stage auditor-access disclosure held as not disclosed. Actor-decision prompt still exposed auditor-access treatment fields. | `H3_raw_hidden_access_integrity` from `runs/source_grounded_raw_access_ab_150/` | `RVS1_summary_not_disclosed_integrity` from `runs/source_grounded_summary_neutral_150/` |
| Original cases, fixed boundary | 150 | Same cases as the initial A/B. Auditor-access fields hidden from actor decision; response-stage disclosure held as not disclosed. | `H3_raw_hidden_access_integrity` from `runs/source_grounded_raw_vs_summary_original_cases_fixed_150/` | `RVS1_summary_not_disclosed_integrity` from `runs/source_grounded_raw_vs_summary_original_cases_fixed_150/` |
| Fresh replication, fixed boundary | 150 | New source-grounded cases. Auditor-access fields hidden from actor decision; response-stage disclosure held as not disclosed. | `H3_raw_hidden_access_integrity` from `runs/source_grounded_raw_vs_summary_fresh_150/` | `RVS1_summary_not_disclosed_integrity` from `runs/source_grounded_raw_vs_summary_fresh_150/` |

All three runs use source-grounded model-card cases, the no-new-evidence argumentation regime, full actor visibility into the initial audit rationale, and the same anti-capture integrity reminder.

## Results

| Run | Arm | PIFC | Overall false compliance |
| --- | --- | ---: | ---: |
| Initial A/B | Summary only | 4/150 = 2.7% (95% CI 1.0%-6.7%) | 4/150 = 2.7% (95% CI 1.0%-6.7%) |
| Initial A/B | Raw evidence | 16/145 = 11.0% (95% CI 6.9%-17.2%) | 21/150 = 14.0% (95% CI 9.3%-20.5%) |
| Original cases, fixed boundary | Summary only | 5/150 = 3.3% (95% CI 1.4%-7.6%) | 5/150 = 3.3% (95% CI 1.4%-7.6%) |
| Original cases, fixed boundary | Raw evidence | 11/144 = 7.6% (95% CI 4.3%-13.2%) | 17/150 = 11.3% (95% CI 7.2%-17.4%) |
| Fresh replication, fixed boundary | Summary only | 9/150 = 6.0% (95% CI 3.2%-11.0%) | 9/150 = 6.0% (95% CI 3.2%-11.0%) |
| Fresh replication, fixed boundary | Raw evidence | 7/142 = 4.9% (95% CI 2.4%-9.8%) | 15/150 = 10.0% (95% CI 6.2%-15.8%) |

## Paired Contrasts

| Run | Metric | Raw only | Summary only | Both | Neither | Exact McNemar p | Raw minus summary |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Initial A/B | PIFC | 14 | 2 | 2 | 132 | 0.00418 | +8.4 pp, approx 95% interval +2.7 to +14.1 pp |
| Initial A/B | Overall false compliance | 18 | 1 | 3 | 128 | 0.000076 | +11.3 pp, approx 95% interval +5.2 to +17.5 pp |
| Original cases, fixed boundary | PIFC | 10 | 4 | 1 | 135 | 0.180 | +4.3 pp, approx 95% interval -0.9 to +9.5 pp |
| Original cases, fixed boundary | Overall false compliance | 15 | 3 | 2 | 130 | 0.00754 | +8.0 pp, approx 95% interval +2.2 to +13.8 pp |
| Fresh replication, fixed boundary | PIFC | 5 | 7 | 2 | 136 | 0.774 | -1.1 pp, approx 95% interval -6.3 to +4.1 pp |
| Fresh replication, fixed boundary | Overall false compliance | 12 | 6 | 3 | 129 | 0.238 | +4.0 pp, approx 95% interval -2.1 to +10.1 pp |

## Reading

Raw evidence access is now a narrower claim. The initial A/B showed a clear raw-over-summary PIFC gap. When the same cases are rerun through the fixed actor-visible boundary, the raw arm remains higher, but the PIFC contrast is uncertain. On fresh cases under the same boundary, the two arms land near parity.

Raw evidence may still raise overall false compliance in some settings. The original-case fixed-boundary rerun has a clearer raw-over-summary overall false-compliance gap than the fresh replication. That is a softer claim than the initial PIFC story and belongs in follow-up work.

The stable mechanism across reviewed failure cases remains caveat conversion: an unresolved requirement is reframed as something to disclose, monitor, or condition, and the final auditor sometimes accepts that as enough.

Canonical artifacts:

- `runs/source_grounded_raw_vs_summary_neutral_150/`
- `runs/source_grounded_summary_neutral_150/`
- `runs/source_grounded_raw_vs_summary_original_cases_fixed_150/`
- `runs/source_grounded_raw_vs_summary_original_cases_fixed_150_comparison/`
- `runs/source_grounded_raw_vs_summary_fresh_150/`
- `runs/source_grounded_raw_vs_summary_fresh_150_comparison/`
