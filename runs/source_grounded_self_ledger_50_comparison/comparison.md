# source_grounded_self_ledger_50

Self-generated concern ledger on fixed-boundary source-grounded cases

## Arm Results

| Arm | Treatment | Transcripts | PIFC denom | PIFC | Overall false compliance |
| --- | --- | ---: | ---: | ---: | ---: |
| Self-ledger workflow, standard final audit | `SL0_self_ledger_standard_final` | 50 | 50 | 4/50 = 8.0% (95% CI 3.2%-18.8%) | 4/50 = 8.0% (95% CI 3.2%-18.8%) |
| Self-ledger workflow, ledger-updating final audit | `SL1_self_ledger_final` | 50 | 50 | 0/50 = 0.0% (95% CI 0.0%-7.1%) | 0/50 = 0.0% (95% CI 0.0%-7.1%) |

## Paired Comparison

| Metric | Left only | Right only | Both | Neither | Exact McNemar p | Left minus right |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| persuasion_induced_false_compliance | 4 | 0 | 0 | 46 | 0.125 | 8.0% (95% approx 0.5%-15.5%) |
| false_compliance | 4 | 0 | 0 | 46 | 0.125 | 8.0% (95% approx 0.5%-15.5%) |
| ledger_escape_pifc | 0 | 0 | 0 | 50 | 1 | 0.0% (95% approx 0.0%-0.0%) |
| ledger_omission_pifc | 4 | 0 | 0 | 46 | 0.125 | 8.0% (95% approx 0.5%-15.5%) |
| ledger_lost_pifc | 4 | 0 | 0 | 46 | 0.125 | 8.0% (95% approx 0.5%-15.5%) |
| unsupported_ledger_closure | 0 | 10 | 0 | 40 | 0.00195312 | -20.0% (95% approx -31.1%--8.9%) |
