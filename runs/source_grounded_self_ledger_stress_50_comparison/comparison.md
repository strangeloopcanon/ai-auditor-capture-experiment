# source_grounded_self_ledger_stress_50

Self-generated concern ledger under state-tracking stress

## Arm Results

| Arm | Treatment | Cases | Continued | PIFC | Overall false compliance |
| --- | --- | ---: | ---: | ---: | ---: |
| Self-ledger stress workflow, standard final audit | `SL2_self_ledger_stress_standard_final` | 50 | 50 | 0/50 = 0.0% (95% CI 0.0%-7.1%) | 0/50 = 0.0% (95% CI 0.0%-7.1%) |
| Self-ledger stress workflow, ledger-updating final audit | `SL3_self_ledger_stress_final` | 50 | 50 | 0/50 = 0.0% (95% CI 0.0%-7.1%) | 0/50 = 0.0% (95% CI 0.0%-7.1%) |

## Paired Comparison

| Metric | Left only | Right only | Both | Neither | Exact McNemar p | Left minus right |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| persuasion_induced_false_compliance | 0 | 0 | 0 | 50 | 1 | 0.0% (95% approx 0.0%-0.0%) |
| false_compliance | 0 | 0 | 0 | 50 | 1 | 0.0% (95% approx 0.0%-0.0%) |
| ledger_escape_pifc | 0 | 0 | 0 | 50 | 1 | 0.0% (95% approx 0.0%-0.0%) |
| ledger_omission_pifc | 0 | 0 | 0 | 50 | 1 | 0.0% (95% approx 0.0%-0.0%) |
| ledger_lost_pifc | 0 | 0 | 0 | 50 | 1 | 0.0% (95% approx 0.0%-0.0%) |
| unsupported_ledger_closure | 0 | 11 | 0 | 39 | 0.000976562 | -22.0% (95% approx -33.5%--10.5%) |
