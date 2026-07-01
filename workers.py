"""inproc 모드에서 백그라운드 워커를 한 번만 기동한다.

Streamlit은 상호작용마다 스크립트를 재실행하므로, 모듈 전역 플래그로
스레드가 중복 생성되지 않도록 가드한다.
"""
import threading
import time

import bus
import topics
import sim_sensors
import cry_classifier
from state_store import store
from fusion import Fusion

_started = False
_lock = threading.Lock()


def _store_writer(topic, payload):
    store.update(topic, payload)


def _sensor_loop():
    while True:
        bus.publish(topics.RADAR, sim_sensors.radar_step())
        bus.publish(topics.ENV, sim_sensors.env_step())
        time.sleep(1)


def _cry_loop():
    while True:
        bus.publish(topics.CRY, cry_classifier.step())
        time.sleep(1)


def ensure_started():
    global _started
    with _lock:
        if _started:
            return
        bus.subscribe("#", _store_writer)          # 모든 토픽 -> 대시보드 저장소
        f = Fusion()
        bus.subscribe(topics.RADAR, f.on_message)
        bus.subscribe(topics.CRY, f.on_message)
        bus.subscribe(topics.ENV, f.on_message)
        threading.Thread(target=_sensor_loop, daemon=True).start()
        threading.Thread(target=_cry_loop, daemon=True).start()
        _started = True
