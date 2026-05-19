# Raw-vs-Summary Neutral Comparison

This comparison holds actor access disclosure fixed as not disclosed and compares summary-only auditor access with raw-evidence auditor access on the same 150 source-grounded cases.

| Arm | Auditor access | Actor access disclosure | PIFC | Overall false compliance |
|---|---|---|---:|---:|
| Summary neutral | summary_only | not_disclosed | 4/150 = 2.7% (95% CI 1.0%-6.7%) | 4/150 = 2.7% (95% CI 1.0%-6.7%) |
| Raw neutral | raw_evidence | not_disclosed | 16/145 = 11.0% (95% CI 6.9%-17.2%) | 21/150 = 14.0% (95% CI 9.3%-20.5%) |

Raw-evidence access is higher than summary-only access by 8.4 percentage points on PIFC, using an approximate independent two-proportion interval of 2.7 to 14.1 percentage points.
On all-case false compliance, raw-evidence access is higher by 11.3 percentage points, with an approximate interval of 5.2 to 17.5 percentage points.

| Paired metric | Raw only | Summary only | Both | Neither | Exact McNemar p |
|---|---:|---:|---:|---:|---:|
| pifc | 14 | 2 | 2 | 132 | 0.00418091 |
| false_compliance | 18 | 1 | 3 | 128 | 7.62939e-05 |
