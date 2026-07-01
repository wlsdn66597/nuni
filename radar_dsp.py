"""레이더 원신호 → 호흡수·움직임·무호흡 추출 (실제 DSP).

FFT 기반 호흡대역 피크 검출. 원신호가 시뮬이든 실물이든 동일 알고리즘을 쓴다.
(MR60BHA2처럼 호흡수를 직접 출력하는 모듈이면 이 DSP는 검증/백업 경로로,
 BGT60TR13C 같은 원신호 모듈이면 이 DSP가 추출기 본체로 동작.)
"""
import numpy as np

BREATHING_BAND = (0.1, 1.0)   # Hz = 6~60회/분 (영유아 포함)
APNEA_AMP = 0.15              # 최근 창 RMS 진폭이 이 이하이면 호흡 미검출(무호흡)
APNEA_WIN_S = 4              # 무호흡 판정용 최근 창(초) - 긴 호흡창과 분리해 반응성 확보
MOVE_GAIN = 4.0              # 움직임 지표 스케일


def analyze(sig, fs):
    """→ {breathing_rate(회/분), amplitude, movement(0~1)}"""
    x0 = np.asarray(sig, dtype=float)
    if len(x0) < 8:
        return {"breathing_rate": 0.0, "amplitude": 0.0, "movement": 0.0}

    x = x0 - np.mean(x0)

    # 무호흡: 최근 APNEA_WIN_S초 창의 RMS 진폭 (긴 창은 짧은 정지를 희석)
    rec = x0[-int(APNEA_WIN_S * fs):] if len(x0) >= APNEA_WIN_S * fs else x0
    amp = float(np.sqrt(np.mean((rec - rec.mean()) ** 2)))

    w = np.hanning(len(x))
    X = np.abs(np.fft.rfft(x * w))
    f = np.fft.rfftfreq(len(x), 1.0 / fs)

    band = (f >= BREATHING_BAND[0]) & (f <= BREATHING_BAND[1])
    br = 0.0
    if band.any() and X[band].max() > 0:
        br = float(f[band][np.argmax(X[band])] * 60.0)   # 호흡수: 긴 창(주파수 해상도)

    # 움직임: 최근 2초 창의 고주파 에너지 비율 (반응성)
    tail = x[-int(2 * fs):] if len(x) >= 2 * fs else x
    Xt = np.abs(np.fft.rfft(tail * np.hanning(len(tail))))
    ft = np.fft.rfftfreq(len(tail), 1.0 / fs)
    band_t = (ft >= BREATHING_BAND[0]) & (ft <= BREATHING_BAND[1])
    hi_t = ft > BREATHING_BAND[1]
    e_band = float((Xt[band_t] ** 2).sum()) + 1e-9
    e_hi = float((Xt[hi_t] ** 2).sum()) if hi_t.any() else 0.0
    movement = float(np.clip(e_hi / (e_band + e_hi) * MOVE_GAIN, 0, 1))

    if amp < APNEA_AMP:            # 무호흡: 호흡 진폭 급감
        br = 0.0

    return {"breathing_rate": round(br, 1), "amplitude": round(amp, 3),
            "movement": round(movement, 2)}
