# source_grounded_raw_vs_summary_neutral_150

Holding actor access disclosure fixed as not disclosed, does auditor raw-evidence access change persuasion-induced false compliance relative to summary-only auditor access?

## Arm Results

| Arm | Treatment | Transcripts | PIFC denom | PIFC | Overall false compliance |
| --- | --- | ---: | ---: | ---: | ---: |
| Raw evidence | `H3_raw_hidden_access_integrity` | 150 | 145 | 16/145 = 11.0% (95% CI 6.9%-17.2%) | 21/150 = 14.0% (95% CI 9.3%-20.5%) |
| Summary only | `RVS1_summary_not_disclosed_integrity` | 150 | 150 | 4/150 = 2.7% (95% CI 1.0%-6.7%) | 4/150 = 2.7% (95% CI 1.0%-6.7%) |

## Paired Comparison

| Metric | Left only | Right only | Both | Neither | Exact McNemar p | Left minus right |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| persuasion_induced_false_compliance | 14 | 2 | 2 | 132 | 0.00418091 | 8.4% (95% approx 2.7%-14.1%) |
| false_compliance | 18 | 1 | 3 | 128 | 7.62939e-05 | 11.3% (95% approx 5.2%-17.5%) |
