# Raw-Access Actor-Knowledge A/B

This focused follow-up isolates the specific mechanism question raised by the hidden-access run:

> When the auditor has raw evidence access, does telling the actor about that access change persuasion-induced false compliance?

The design keeps the source-grounded model-card lane, integrity reminder, no-new-evidence persuasion regime, and full initial-audit rationale visibility fixed. The only intended difference is actor knowledge of auditor raw evidence access.

| Arm | Auditor access | Actor access disclosure |
|---|---|---|
| `H3_raw_hidden_access_integrity` | Raw evidence | Not disclosed |
| `H4_raw_known_access_integrity` | Raw evidence | Told raw access |

The first `25` cases come from the completed hidden-access run. The next `25` cases are source-grounded extensions that reuse the same public Hugging Face/NIST governance grounding and add new repo-local launch artifacts. Because the 50-case result remained directionally interesting, the final checked output adds another 25 source-grounded extensions for a 75-case paired read.

## Results

| Run | Arm | PIFC | Overall false compliance |
|---|---|---:|---:|
| 50 paired cases | H3 raw / not disclosed | 5/49 = 10.2% (95% CI 4.4%-21.8%) | 6/50 = 12.0% (95% CI 5.6%-23.8%) |
| 50 paired cases | H4 raw / told raw | 1/48 = 2.1% (95% CI 0.4%-10.9%) | 3/50 = 6.0% (95% CI 2.1%-16.2%) |
| 75 paired cases | H3 raw / not disclosed | 9/74 = 12.2% (95% CI 6.5%-21.5%) | 10/75 = 13.3% (95% CI 7.4%-22.8%) |
| 75 paired cases | H4 raw / told raw | 2/73 = 2.7% (95% CI 0.8%-9.5%) | 4/75 = 5.3% (95% CI 2.1%-12.9%) |

The current signal is not that shared raw evidence makes agreement easier in every condition. The cleaner statement is narrower: when the auditor has raw evidence, telling the actor that fact reduced persuasion-induced false compliance in this source-grounded setup.

Run a new 25-case extension batch:

```bash
python3 scripts/run_experiment.py \
  --cases data/cases_source_grounded_raw_access_ab_extension_25.jsonl \
  --treatments config/treatments.raw_access_ab_integrity.json \
  --manifest config/run_manifest.mvp.json \
  --out runs/source_grounded_raw_access_ab_extension_25 \
  --assignment all_conditions \
  --execute
```

The combined 50-case output folder is `runs/source_grounded_raw_access_ab_50`.

The combined 75-case output folder is `runs/source_grounded_raw_access_ab_75`.
