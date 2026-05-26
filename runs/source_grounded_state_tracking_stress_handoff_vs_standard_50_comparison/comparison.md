# source_grounded_state_tracking_stress_handoff_vs_standard_50

Does compressed handoff differ from standard final audit under state-tracking stress?

## Arm Results

| Arm | Treatment | Cases | Continued | PIFC | Overall false compliance |
| --- | --- | ---: | ---: | ---: | ---: |
| Compressed handoff final audit | `ST3_raw_state_tracking_stress_handoff_integrity` | 50 | 50 | 1/50 = 2.0% (95% CI 0.4%-10.5%) | 1/50 = 2.0% (95% CI 0.4%-10.5%) |
| Standard final audit | `ST1_raw_state_tracking_stress_integrity` | 50 | 50 | 1/50 = 2.0% (95% CI 0.4%-10.5%) | 1/50 = 2.0% (95% CI 0.4%-10.5%) |

## Paired Comparison

| Metric | Left only | Right only | Both | Neither | Exact McNemar p | Left minus right |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| persuasion_induced_false_compliance | 1 | 1 | 0 | 48 | 1 | 0.0% (95% approx -5.5%-5.5%) |
| false_compliance | 1 | 1 | 0 | 48 | 1 | 0.0% (95% approx -5.5%-5.5%) |
