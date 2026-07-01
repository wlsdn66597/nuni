"""합성 레이더 원신호 생성기 (호흡 DSP 검증용 GT 소스).

설정한 BPM/움직임/무호흡이 곧 정답(Ground Truth)이 되므로, radar_dsp가
얼마나 정확히 복원하는지 오차를 정량화할 수 있다.
실물 교체 지점: RadarSource.next_chunk() 대신 60GHz 모듈의 원신호를 읽으면 된다.
"""
import numpy as np


class RadarSource:
    """연속 위상을 유지하며 원신호 청크를 스트리밍한다."""

    def __init__(self, fs=20, seed=0):
        self.fs = fs
        self.i = 0
        self.rng = np.random.default_rng(seed)

    def next_chunk(self, seconds, bpm, amp=1.0, snr_db=20, motion=0.0):
        n = int(self.fs * seconds)
        t = (self.i + np.arange(n)) / self.fs
        self.i += n
        sig = amp * np.sin(2 * np.pi * (bpm / 60.0) * t)   # 호흡 성분
        if motion > 0:
            sig = sig + motion * np.sin(2 * np.pi * 4.0 * t)  # 4Hz 움직임 성분
        p = np.mean(sig ** 2) + 1e-9
        noise = self.rng.standard_normal(n)
        k = np.sqrt(p / (10 ** (snr_db / 10)) / (np.mean(noise ** 2) + 1e-9))
        return sig + k * noise


def make_window(bpm, fs=20, seconds=30, amp=1.0, snr_db=15, seed=0):
    """단발 윈도우 생성 (eval_radar 용)."""
    return RadarSource(fs=fs, seed=seed).next_chunk(seconds, bpm, amp=amp, snr_db=snr_db)
