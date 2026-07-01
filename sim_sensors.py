"""가상 센서 발행자 (레이더 + 환경).

실물 교체 지점:
  - 레이더: MR60BHA2 등 60GHz 모듈의 UART 출력을 파싱해 radar_msg()로 발행
  - 환경:  SCD41(CO2) / BME680 / BH1750(조도) 값을 env_msg()로 발행
토픽/포맷이 동일하므로 아래 radar_step()/env_step() 내부만 실물 읽기로 바꾸면 된다.
"""
import random
import time

import topics
import bus
from state_store import store


def radar_step() -> dict:
    inj = store.active_injects()
    if "apnea" in inj:                       # 무호흡 시나리오
        br = random.uniform(0, 4)
    else:
        br = random.gauss(40, 3)             # 영유아 정상 호흡 ~40회/분
    movement = random.uniform(0, 0.2)
    if random.random() < 0.05:               # 가끔 뒤척임
        movement = random.uniform(0.6, 1.0)
    return topics.radar_msg(round(br, 1), round(movement, 2), True)


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
