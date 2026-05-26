# source_grounded_raw_accounting_fixed_150

Concern accounting on fixed-boundary raw-access interactions

## Arm Results

| Arm | Treatment | Cases | Continued | PIFC | Overall false compliance |
| --- | --- | ---: | ---: | ---: | ---: |
| Standard final audit | `H3_raw_hidden_access_integrity` | 150 | 143 | 6/143 = 4.2% (95% CI 1.9%-8.9%) | 13/150 = 8.7% (95% CI 5.1%-14.3%) |
| Concern accounting final audit | `M1_raw_hidden_integrity` | 150 | 143 | 0/143 = 0.0% (95% CI 0.0%-2.6%) | 7/150 = 4.7% (95% CI 2.3%-9.3%) |

## Paired Comparison

| Metric | Left only | Right only | Both | Neither | Exact McNemar p | Left minus right |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| persuasion_induced_false_compliance | 6 | 0 | 0 | 144 | 0.03125 | 4.2% (95% approx 0.9%-7.5%) |
| false_compliance | 6 | 0 | 7 | 137 | 0.03125 | 4.0% (95% approx -1.6%-9.6%) |
