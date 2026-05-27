# source_grounded_self_ledger_150

Self-generated concern ledger on fixed-boundary source-grounded cases

## Arm Results

| Arm | Treatment | Cases | Continued | PIFC | Overall false compliance |
| --- | --- | ---: | ---: | ---: | ---: |
| Self-ledger workflow, standard final audit | `SL0_self_ledger_standard_final` | 150 | 149 | 8/149 = 5.4% (95% CI 2.7%-10.2%) | 9/150 = 6.0% (95% CI 3.2%-11.0%) |
| Self-ledger workflow, ledger-updating final audit | `SL1_self_ledger_final` | 150 | 149 | 2/149 = 1.3% (95% CI 0.4%-4.8%) | 3/150 = 2.0% (95% CI 0.7%-5.7%) |

## Paired Comparison

| Metric | Left only | Right only | Both | Neither | Exact McNemar p | Left minus right |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| persuasion_induced_false_compliance | 6 | 0 | 2 | 142 | 0.03125 | 4.0% (95% approx -0.0%-8.1%) |
| false_compliance | 6 | 0 | 3 | 141 | 0.03125 | 4.0% (95% approx -0.4%-8.4%) |
| ledger_escape_pifc | 0 | 2 | 0 | 148 | 0.5 | -1.3% (95% approx -3.2%-0.5%) |
| ledger_omission_pifc | 6 | 0 | 1 | 143 | 0.03125 | 4.0% (95% approx 0.4%-7.7%) |
| ledger_lost_pifc | 8 | 0 | 0 | 142 | 0.0078125 | 5.4% (95% approx 1.7%-9.0%) |
| unsupported_ledger_closure | 0 | 34 | 0 | 116 | 1.16415e-10 | -22.7% (95% approx -29.4%--16.0%) |
