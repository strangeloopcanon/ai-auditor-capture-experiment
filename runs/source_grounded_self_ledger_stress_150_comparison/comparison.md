# source_grounded_self_ledger_stress_150

Self-generated concern ledger under state-tracking stress

## Arm Results

| Arm | Treatment | Transcripts | PIFC denom | PIFC | Overall false compliance |
| --- | --- | ---: | ---: | ---: | ---: |
| Self-ledger stress workflow, standard final audit | `SL2_self_ledger_stress_standard_final` | 150 | 148 | 3/148 = 2.0% (95% CI 0.7%-5.8%) | 5/150 = 3.3% (95% CI 1.4%-7.6%) |
| Self-ledger stress workflow, ledger-updating final audit | `SL3_self_ledger_stress_final` | 150 | 148 | 0/148 = 0.0% (95% CI 0.0%-2.5%) | 2/150 = 1.3% (95% CI 0.4%-4.7%) |

## Paired Comparison

| Metric | Left only | Right only | Both | Neither | Exact McNemar p | Left minus right |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| persuasion_induced_false_compliance | 3 | 0 | 0 | 147 | 0.25 | 2.0% (95% approx -0.2%-4.3%) |
| false_compliance | 3 | 0 | 2 | 145 | 0.25 | 2.0% (95% approx -1.4%-5.4%) |
| ledger_escape_pifc | 0 | 0 | 0 | 150 | 1 | 0.0% (95% approx 0.0%-0.0%) |
| ledger_omission_pifc | 3 | 0 | 0 | 147 | 0.25 | 2.0% (95% approx -0.2%-4.3%) |
| ledger_lost_pifc | 3 | 0 | 0 | 147 | 0.25 | 2.0% (95% approx -0.2%-4.3%) |
| unsupported_ledger_closure | 0 | 52 | 0 | 98 | 4.44089e-16 | -34.7% (95% approx -42.3%--27.1%) |
