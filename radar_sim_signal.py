"""Synthetic radar-like raw signal generator for software-only tests.

This module does not model a specific 60GHz radar device. It creates simple
raw displacement-like signals with breathing, optional motion bursts, apnea
segments, and additive noise so the DSP path can be tested without hardware.
"""
import numpy as np


def _add_awgn(signal, snr_db, rng):
    power = float(np.mean(signal ** 2))
    if power <= 1e-12:
        power = 1e-12
    noise_power = power / (10 ** (snr_db / 10))
    return signal + rng.normal(0.0, np.sqrt(noise_power), size=signal.shape)


def generate_breathing_signal(
    duration_s=30,
    fs=50,
    bpm=30,
    snr_db=15,
    motion=False,
    apnea_start=None,
    apnea_duration=None,
    seed=0,
):
    """Generate a synthetic raw radar-like signal.

    Returns:
        (t, signal, metadata)
    """
    rng = np.random.default_rng(seed)
    n = int(duration_s * fs)
    t = np.arange(n, dtype=float) / fs
    freq_hz = bpm / 60.0

    envelope = np.ones_like(t)
    if apnea_start is not None and apnea_duration is not None:
        apnea_end = apnea_start + apnea_duration
        mask = (t >= apnea_start) & (t < apnea_end)
        envelope[mask] = 0.03

    breathing = envelope * np.sin(2 * np.pi * freq_hz * t)
    harmonic = 0.08 * envelope * np.sin(2 * np.pi * 2 * freq_hz * t + 0.4)
    drift = 0.05 * np.sin(2 * np.pi * 0.03 * t)
    raw = breathing + harmonic + drift

    if motion:
        center = duration_s - 1.0
        burst_width = 0.30
        burst_env = np.exp(-0.5 * ((t - center) / burst_width) ** 2)
        burst = 1.8 * burst_env * np.sin(2 * np.pi * 4.0 * t)
        raw = raw + burst

    raw = _add_awgn(raw, snr_db, rng)
    metadata = {
        "duration_s": duration_s,
        "fs": fs,
        "true_bpm": bpm,
        "snr_db": snr_db,
        "motion": bool(motion),
        "apnea_start": apnea_start,
        "apnea_duration": apnea_duration,
        "source": "synthetic_raw_signal",
    }
    return t, raw.astype(float), metadata


def generate_eval_cases():
    """Return deterministic BPM test cases for synthetic DSP evaluation."""
    return [
        {"duration_s": 30, "fs": 50, "bpm": bpm, "snr_db": 15, "seed": i}
        for i, bpm in enumerate([20, 25, 30, 35, 40, 45])
    ]
