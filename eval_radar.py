"""호흡수 추출 DSP 검증 (설정 BPM = GT 와 비교).

실행: python eval_radar.py
결과: BPM별 추정 오차 표 + MAE (보고서 "호흡 추정 정확도"에 사용)
"""
import numpy as np

import radar_sim_signal as rs
import radar_dsp

FS = 20
SECONDS = 30


def main():
    print(f"{'설정BPM':<10}{'추정BPM':<10}{'오차':<8}")
    print("-" * 28)
    errs, pairs = [], []
    for bpm in [20, 25, 30, 35, 40, 45, 50, 55]:
        sig = rs.make_window(bpm, fs=FS, seconds=SECONDS, snr_db=15, seed=bpm)
        est = radar_dsp.analyze(sig, FS)["breathing_rate"]
        err = abs(est - bpm)
        errs.append(err); pairs.append((bpm, est))
        print(f"{bpm:<10}{est:<10}{round(err, 1):<8}")
    print("-" * 28)
    print(f"MAE: {round(float(np.mean(errs)), 2)} 회/분  (윈도우 {SECONDS}s, SNR 15dB)")
    print("Bland-Altman용 (설정,추정):", pairs)


if __name__ == "__main__":
    main()
