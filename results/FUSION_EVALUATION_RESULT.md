# Fusion Evaluation Result

- Controlled scenarios: 8
- Metrics are computed from this script at runtime.

## Policy Summary

| policy | false alarm | miss |
|---|---:|---:|
| single_sensor | 5 | 0 |
| radar_only | 0 | 0 |
| audio_only | 2 | 1 |
| env_only | 2 | 2 |
| full_fusion | 0 | 0 |

## Interpretation

The full fusion policy treats radar apnea as a strong risk signal, uses cry as a supporting signal, and treats environment as context. Single-modality policies are intentionally simpler and can over-alert on isolated signals.

## Limits

- This is a controlled software scenario evaluation, not a real sensor or clinical test.
- Debounce/cooldown behavior is implemented in the live `Fusion` subscriber, not in this stateless scenario table.
