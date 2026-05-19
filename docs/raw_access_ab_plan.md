# Raw-Access Actor-Knowledge A/B

This focused A/B isolates the actor-knowledge mechanism tested after the hidden-access run:

> When the auditor has raw evidence access, does telling the actor about that access change persuasion-induced false compliance?

The design keeps the source-grounded model-card lane, integrity reminder, no-new-evidence persuasion regime, and full initial-audit rationale visibility fixed. The only intended difference is actor knowledge of auditor raw evidence access.

| Arm | Auditor access | Actor access disclosure |
|---|---|---|
| `H3_raw_hidden_access_integrity` | Raw evidence | Not disclosed |
| `H4_raw_known_access_integrity` | Raw evidence | Told raw access |

The first `25` cases come from the completed hidden-access run. The extension cases reuse the same public Hugging Face/NIST governance grounding and add new repo-local launch artifacts. The checked output now includes 50, 75, and 150 paired-case reads.

## Results

| Run | Arm | PIFC | Overall false compliance |
|---|---|---:|---:|
| 50 paired cases | H3 raw / not disclosed | 5/49 = 10.2% (95% CI 4.4%-21.8%) | 6/50 = 12.0% (95% CI 5.6%-23.8%) |
| 50 paired cases | H4 raw / told raw | 1/48 = 2.1% (95% CI 0.4%-10.9%) | 3/50 = 6.0% (95% CI 2.1%-16.2%) |
| 75 paired cases | H3 raw / not disclosed | 9/74 = 12.2% (95% CI 6.5%-21.5%) | 10/75 = 13.3% (95% CI 7.4%-22.8%) |
| 75 paired cases | H4 raw / told raw | 2/73 = 2.7% (95% CI 0.8%-9.5%) | 4/75 = 5.3% (95% CI 2.1%-12.9%) |
| 150 paired cases | H3 raw / not disclosed | 16/145 = 11.0% (95% CI 6.9%-17.2%) | 21/150 = 14.0% (95% CI 9.3%-20.5%) |
| 150 paired cases | H4 raw / told raw | 8/147 = 5.4% (95% CI 2.8%-10.4%) | 11/150 = 7.3% (95% CI 4.1%-12.7%) |

The 150-case extension preserves the direction of the actor-knowledge effect while attenuating its size. Disclosed auditor raw-evidence access is associated with lower PIFC in this setup. The direct raw-vs-summary access contrast is tested separately in `docs/raw_vs_summary_neutral.md`.

Canonical output folders:

- `runs/source_grounded_raw_access_ab_50`
- `runs/source_grounded_raw_access_ab_75`
- `runs/source_grounded_raw_access_ab_150`
