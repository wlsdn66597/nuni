# NUNI Software Verification Results

## Environment

- Python: 3.10.12
- Git commit: `a114412401fdb6b88d9c40a8831f8fbac22b833b`
- Generated at: 2026-07-01 22:49:37

## Summary

| Area | Result | Artifact |
|---|---|---|
| Basic validation | compileall success | `results/logs/compileall.log` |
| Radar DSP | synthetic BPM MAE 0.5 breaths/min | `results/RADAR_DSP_RESULT.md` |
| Fusion | full fusion false alarm 0, miss 0 | `results/FUSION_EVALUATION_RESULT.md` |
| Single baseline | false alarm 5, miss 0 | `results/artifacts/fusion_ablation_summary.csv` |
| Dashboard | import smoke success | `results/logs/dashboard_import_smoke.log` |
| Cry ML | existing reports summarize limited reason-classifier performance | `reports/FINAL_CRY_MODEL_DECISION.md` |

## Limits

- Radar DSP is evaluated only on synthetic raw radar-like signals.
- This run does not validate real 60GHz radar hardware.
- Cry detection results in reports use synthetic negative audio for smoke testing.
- Donate-a-Cry 5-class reason classification remains limited by class imbalance.
