"""가상 센서 발행자 (레이더 + 환경).

실물 교체 지점:
  - 레이더: MR60BHA2 등 60GHz 모듈의 UART 출력을 파싱해 radar_msg()로 발행
  - 환경:  SCD41(CO2) / BME680 / BH1750(조도) 값을 env_msg()로 발행
토픽/포맷이 동일하므로 아래 radar_step()/env_step() 내부만 실물 읽기로 바꾸면 된다.
"""
import random
import time
import collections

import topics
import bus
import radar_dsp
import radar_sim_signal
from state_store import store

# 원신호 스트리밍 버퍼: 실제 DSP가 호흡수를 추출한다.
_FS = 20
_WINDOW_S = 20
_src = radar_sim_signal.RadarSource(fs=_FS)
_buf = collections.deque(maxlen=_FS * _WINDOW_S)


def radar_step() -> dict:
    inj = store.active_injects()
    # === 실물 교체 지점 ===
    # 아래 next_chunk(합성 원신호) 대신 60GHz 모듈의 원신호 1초를 읽어 _buf.extend() 하면
    # radar_dsp.analyze()는 그대로 실물 신호를 처리한다.
    if "apnea" in inj:                                   # 무호흡: 진폭 급감
        chunk = _src.next_chunk(1.0, bpm=40, amp=0.05)
    else:
        bpm = random.gauss(40, 2)                        # 영유아 정상 ~40회/분
        motion = random.uniform(0.6, 1.0) if random.random() < 0.05 else 0.0  # 뒤척임
        chunk = _src.next_chunk(1.0, bpm=bpm, amp=1.0, motion=motion)
    _buf.extend(chunk)

    r = radar_dsp.analyze(list(_buf), _FS)               # 실제 호흡 DSP
    return topics.radar_msg(r["breathing_rate"], r["movement"], True)


def env_step() -> dict:
    co2 = max(400, int(random.gauss(650, 80)))
    return topics.env_msg(
        round(random.gauss(22, 0.5), 1),     # 온도
        round(random.gauss(45, 3)),          # 습도
        co2,                                 # CO2
        round(random.uniform(5, 30), 1),     # 조도(야간)
    )


def run():
    """분산(MQTT) 모드에서 독립 프로세스로 실행할 때 사용."""
    while True:
        bus.publish(topics.RADAR, radar_step())
        bus.publish(topics.ENV, env_step())
        time.sleep(1)


if __name__ == "__main__":
    run()
