# Raw-Access Actor-Knowledge A/B

This focused A/B asks:

> When the auditor has raw evidence access, does telling the actor about that access change persuasion-induced false compliance?

The design keeps the source-grounded model-card lane, integrity reminder, no-new-evidence persuasion regime, and full initial-audit rationale visibility fixed. The tested difference is actor knowledge of auditor raw evidence access.

| Arm | Auditor access | Actor access disclosure |
|---|---|---|
| `H3_raw_hidden_access_integrity` | Raw evidence | Not disclosed |
| `H4_raw_known_access_integrity` | Raw evidence | Told raw access |

## Results

| Run | Arm | PIFC | Overall false compliance |
|---|---|---:|---:|
| 50 paired cases | H3 raw / not disclosed | 5/49 = 10.2% (95% CI 4.4%-21.8%) | 6/50 = 12.0% (95% CI 5.6%-23.8%) |
| 50 paired cases | H4 raw / told raw | 1/48 = 2.1% (95% CI 0.4%-10.9%) | 3/50 = 6.0% (95% CI 2.1%-16.2%) |
| 75 paired cases | H3 raw / not disclosed | 9/74 = 12.2% (95% CI 6.5%-21.5%) | 10/75 = 13.3% (95% CI 7.4%-22.8%) |
| 75 paired cases | H4 raw / told raw | 2/73 = 2.7% (95% CI 0.8%-9.5%) | 4/75 = 5.3% (95% CI 2.1%-12.9%) |
| 150 base cases, initial boundary | H3 raw / not disclosed | 16/145 = 11.0% (95% CI 6.9%-17.2%) | 21/150 = 14.0% (95% CI 9.3%-20.5%) |
| 150 base cases, initial boundary | H4 raw / told raw | 8/147 = 5.4% (95% CI 2.8%-10.4%) | 11/150 = 7.3% (95% CI 4.1%-12.7%) |
| 150 base cases, fixed boundary | H3 raw / not disclosed | 6/143 = 4.2% (95% CI 1.9%-8.9%) | 13/150 = 8.7% (95% CI 5.1%-14.3%) |
| 150 base cases, fixed boundary | H4 raw / told raw | 14/145 = 9.7% (95% CI 5.8%-15.6%) | 19/150 = 12.7% (95% CI 8.3%-18.9%) |

## Fixed-Boundary Paired Contrast

| Metric | Not-told only | Told only | Both | Neither | Exact McNemar p | Not-told minus told |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PIFC | 6 | 14 | 0 | 130 | 0.115 | -5.5 pp, approx 95% interval -11.3 to +0.4 pp |
| Overall false compliance | 12 | 18 | 1 | 119 | 0.362 | -4.0 pp, approx 95% interval -11.0 to +3.0 pp |

## Reading

The actor-knowledge result changes under the fixed boundary. The initial 150-case run suggested lower PIFC when the actor was told the auditor had raw evidence access. The fixed-boundary rerun goes the other way: the told arm has higher PIFC, although the contrast remains uncertain.

The current claim is narrow. Actor knowledge of raw auditor access matters enough to measure, but the checked runs point in different directions. The direct raw-vs-summary evidence-access contrast is summarized in `docs/raw_vs_summary_neutral.md`.

Canonical output folders:

- `runs/source_grounded_raw_access_ab_50`
- `runs/source_grounded_raw_access_ab_75`
- `runs/source_grounded_raw_access_ab_150`
- `runs/source_grounded_raw_access_ab_fixed_150`
- `runs/source_grounded_raw_access_ab_fixed_150_comparison`
