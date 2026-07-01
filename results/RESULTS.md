# NUNI Software Verification Results

## Environment

- Python: 3.10.12
- Git commit: `1d2b5f5f2ae027663d200226e58bd93ea3bb7c1d`
- Generated at: 2026-07-02 03:19:50

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
| Sleep/wake state | classification accuracy 100% | `results/SLEEP_STATE_RESULT.md` |
| Personalization | per-household baseline adaptation | `results/PERSONALIZATION_RESULT.md` |
| Environment control | action match 100% | `results/ENV_CONTROL_RESULT.md` |
| Voice intent | keyword intent recognition | `results/VOICE_INTENT_RESULT.md` |
| Cloud sleep report | overnight summary + personalized range | `results/SLEEP_REPORT.md` |
| Dashboard | import smoke success | `results/logs/dashboard_import_smoke.log` |
| Cry ML | limited reason-classifier (class imbalance) | `results/CRY_CLASSIFICATION_LIMITATION.md` |

## Positioning

- Main tasks: everyday non-contact monitoring (sleep/wake state, cry detection,
  environment) + proactive control + personalization.
- Apnea/breathing-abnormality is a rare safety backup, not the headline, and is not
  a medical-grade claim.

## Limits

- All results are synthetic/controlled software validation, not real sensors/infants.
- Cry reason classification stays experimental (class imbalance).
- Environment control emits recommendations; real actuation is a 2nd-round hardware step.
