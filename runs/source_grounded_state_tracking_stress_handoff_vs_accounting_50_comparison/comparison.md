# source_grounded_state_tracking_stress_handoff_vs_accounting_50

Does exact concern accounting beat compressed handoff under state-tracking stress?

## Arm Results

| Arm | Treatment | Transcripts | PIFC denom | PIFC | Overall false compliance |
| --- | --- | ---: | ---: | ---: | ---: |
| Compressed handoff final audit | `ST3_raw_state_tracking_stress_handoff_integrity` | 50 | 50 | 1/50 = 2.0% (95% CI 0.4%-10.5%) | 1/50 = 2.0% (95% CI 0.4%-10.5%) |
| Exact concern accounting final audit | `ST2_raw_state_tracking_stress_accounting_integrity` | 50 | 50 | 0/50 = 0.0% (95% CI 0.0%-7.1%) | 0/50 = 0.0% (95% CI 0.0%-7.1%) |

## Paired Comparison

| Metric | Left only | Right only | Both | Neither | Exact McNemar p | Left minus right |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| persuasion_induced_false_compliance | 1 | 0 | 0 | 49 | 1 | 2.0% (95% approx -1.9%-5.9%) |
| false_compliance | 1 | 0 | 0 | 49 | 1 | 2.0% (95% approx -1.9%-5.9%) |
