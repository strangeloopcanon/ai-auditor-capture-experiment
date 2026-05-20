# source_grounded_raw_accounting_vs_standard_150

Holding the same raw-access actor response fixed, does unresolved-concern accounting in the final audit reduce persuasion-induced false compliance?

## Arm Results

| Arm | Treatment | Cases | Continued | PIFC | Overall false compliance |
| --- | --- | ---: | ---: | ---: | ---: |
| Concern accounting | `M1_raw_hidden_integrity` | 150 | 145 | 2/145 = 1.4% (95% CI 0.4%-4.9%) | 7/150 = 4.7% (95% CI 2.3%-9.3%) |
| Standard raw evidence | `H3_raw_hidden_access_integrity` | 150 | 145 | 16/145 = 11.0% (95% CI 6.9%-17.2%) | 21/150 = 14.0% (95% CI 9.3%-20.5%) |

## Paired Comparison

| Metric | Left only | Right only | Both | Neither | Exact McNemar p | Left minus right |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| persuasion_induced_false_compliance | 1 | 15 | 1 | 133 | 0.000518799 | -9.7% (95% approx -15.1%--4.2%) |
| false_compliance | 1 | 15 | 6 | 128 | 0.000518799 | -9.3% (95% approx -15.8%--2.8%) |
