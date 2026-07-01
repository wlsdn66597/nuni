# NUNI Software Verification Results

## Environment

- Python: 3.9.7
- Git commit: `3d11c5fc76ac2aa1804b912ed180cce0256ea4da`
- Generated at: 2026-07-01 23:33:21

## Summary

| Area | Result | Artifact |
|---|---|---|
| Basic validation | compileall success | `results/logs/compileall.log` |
| Radar DSP | synthetic BPM MAE 0.5 breaths/min | `results/RADAR_DSP_RESULT.md` |
| Radar robustness | SNR x window MAE sweep | `results/RADAR_ROBUSTNESS_RESULT.md` |
| Fusion | full fusion false alarm 0, miss 0 | `results/FUSION_EVALUATION_RESULT.md` |
| Fusion vs radar-only | radar-only miss 2 (fusion catches) | `results/artifacts/fusion_ablation_summary.csv` |
| Single baseline | false alarm 6, miss 0 | `results/artifacts/fusion_ablation_summary.csv` |
| Streaming (debounce/cooldown) | alerts 4->1, apnea latency 1s | `results/STREAM_EVAL_RESULT.md` |
| Voice intent | keyword intent recognition | `results/VOICE_INTENT_RESULT.md` |
| Cloud sleep report | overnight summary generated | `results/SLEEP_REPORT.md` |
| Dashboard | import smoke success | `results/logs/dashboard_import_smoke.log` |
| Cry ML | limited reason-classifier (class imbalance) | `results/CRY_CLASSIFICATION_LIMITATION.md` |

## Limits

- Radar DSP is evaluated only on synthetic raw radar-like signals.
- Streaming/fusion results use controlled synthetic timelines, not real sensors.
- Voice intent accuracy is on a curated phrase set; real STT/noise will differ.
- Cloud sleep report uses a synthetic night, not real infant data.
- Donate-a-Cry 5-class reason classification remains limited by class imbalance.
