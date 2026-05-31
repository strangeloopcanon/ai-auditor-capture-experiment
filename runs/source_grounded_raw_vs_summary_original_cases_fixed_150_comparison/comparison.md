# source_grounded_raw_vs_summary_original_cases_fixed_150

Phase 3 original cases after actor-visible treatment boundary fix

## Arm Results

| Arm | Treatment | Transcripts | PIFC denom | PIFC | Overall false compliance |
| --- | --- | ---: | ---: | ---: | ---: |
| Raw evidence | `H3_raw_hidden_access_integrity` | 150 | 144 | 11/144 = 7.6% (95% CI 4.3%-13.2%) | 17/150 = 11.3% (95% CI 7.2%-17.4%) |
| Summary only | `RVS1_summary_not_disclosed_integrity` | 150 | 150 | 5/150 = 3.3% (95% CI 1.4%-7.6%) | 5/150 = 3.3% (95% CI 1.4%-7.6%) |

## Paired Comparison

| Metric | Left only | Right only | Both | Neither | Exact McNemar p | Left minus right |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| persuasion_induced_false_compliance | 10 | 4 | 1 | 135 | 0.179565 | 4.3% (95% approx -0.9%-9.5%) |
| false_compliance | 15 | 3 | 2 | 130 | 0.00753784 | 8.0% (95% approx 2.2%-13.8%) |
