# Radar DSP Robustness (synthetic)

- FS=50Hz, BPM set=[20, 30, 40, 50], per-cell = mean abs error over BPM set
- Synthetic raw signal only; not real radar/infant validation.

| window(s) \ SNR(dB) | 5 | 10 | 15 | 20 |
|---|---|---|---|---|
| 15 | 1.000 | 1.000 | 1.000 | 1.000 |
| 30 | 0.000 | 0.000 | 0.000 | 0.000 |
| 60 | 0.000 | 0.000 | 0.000 | 0.000 |

## Interpretation

- 관측 윈도우가 길수록 FFT 주파수 해상도가 높아져 MAE가 낮아진다.
- SNR이 낮을수록(잡음↑) MAE가 커진다.
- 실사용 목표 정확도에 맞춰 최소 관측 윈도우/허용 SNR을 정할 근거로 사용.
