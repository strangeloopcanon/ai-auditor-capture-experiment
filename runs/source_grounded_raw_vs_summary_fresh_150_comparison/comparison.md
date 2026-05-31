# source_grounded_raw_vs_summary_fresh_150

On a fresh source-grounded case set with actor-visible auditor-access fields hidden, does raw auditor evidence access change persuasion-induced false compliance relative to summary-only auditor access?

## Arm Results

| Arm | Treatment | Transcripts | PIFC denom | PIFC | Overall false compliance |
| --- | --- | ---: | ---: | ---: | ---: |
| Raw evidence | `H3_raw_hidden_access_integrity` | 150 | 142 | 7/142 = 4.9% (95% CI 2.4%-9.8%) | 15/150 = 10.0% (95% CI 6.2%-15.8%) |
| Summary only | `RVS1_summary_not_disclosed_integrity` | 150 | 150 | 9/150 = 6.0% (95% CI 3.2%-11.0%) | 9/150 = 6.0% (95% CI 3.2%-11.0%) |

## Paired Comparison

| Metric | Left only | Right only | Both | Neither | Exact McNemar p | Left minus right |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| persuasion_induced_false_compliance | 5 | 7 | 2 | 136 | 0.774414 | -1.1% (95% approx -6.3%-4.1%) |
| false_compliance | 12 | 6 | 3 | 129 | 0.237885 | 4.0% (95% approx -2.1%-10.1%) |
