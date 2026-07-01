"""멀티모달 융합 판단 엔진.

decide(): 레이더+음향+환경을 교차검증하는 규칙 (핵심 차별점)
single_sensor_decide(): 비교용 단일 센서 단순 정책 (오탐이 많음)
-> eval_fusion.py 에서 둘을 비교해 "융합이 오탐을 줄인다"를 정량화.
"""
import topics
import bus
from state_store import store

_ORDER = {"normal": 0, "attention": 1, "alert": 2}


def _max(a, b):
    return a if _ORDER[a] >= _ORDER[b] else b


def decide(radar, cry, env):
    """(level, reasons) 반환. level: normal/attention/alert"""
    level, reasons = "normal", []

    if radar and radar.get("presence") and radar.get("breathing_rate", 99) < 8:
        level = _max(level, "alert")
        reasons.append("호흡 미검출·무호흡 의심")

    cry_flag = bool(cry and cry.get("is_crying") and cry.get("confidence", 0) >= 0.7)
    if cry_flag:
        level = _max(level, "attention")
        reasons.append(f"울음 감지({cry.get('cls')})")

    # 교차검증: 울음 + (호흡 이상 or 큰 움직임)이 동시일 때만 경보로 상향
    if cry_flag and radar and (radar.get("movement", 0) > 0.6 or radar.get("breathing_rate", 99) < 8):
        level = _max(level, "alert")
        reasons.append("다중 신호 동시 이상")

    if env:
        if env.get("co2", 0) > 1000:
            level = _max(level, "attention")
            reasons.append("CO₂ 높음")
        t = env.get("temp")
        if t is not None and (t < 18 or t > 26):
            level = _max(level, "attention")
            reasons.append("실내 온도 이상")

    return level, reasons


def single_sensor_decide(radar, cry, env):
    """비교용: 개별 신호 하나만으로 경보 -> 오탐/미탐 많음."""
    if cry and cry.get("is_crying"):
        return "alert", ["울음(단일)"]
    if radar and radar.get("movement", 0) > 0.5:
        return "alert", ["움직임(단일)"]
    if env and env.get("co2", 0) > 800:
        return "alert", ["CO₂(단일)"]
    return "normal", []


DEBOUNCE = 2        # 비정상이 연속 N회일 때만 확정 (일시적 튐 억제)
COOLDOWN_S = 10     # 동일 경보 반복 알림 억제 구간(초)


class Fusion:
    """라이브 구독자: 최신 신호를 모아 판단하고 상태/경보를 발행.

    decide()(순수 규칙) 위에 시간 디바운스와 쿨다운을 얹어 알림 피로를 줄인다.
    """

    def __init__(self):
        self.radar = self.cry = self.env = None
        self.confirmed = "normal"
        self._streak = 0
        self._last_alert_ts = 0.0

    def on_message(self, topic, payload):
        if topic == topics.RADAR:
            self.radar = payload
        elif topic == topics.CRY:
            self.cry = payload
        elif topic == topics.ENV:
            self.env = payload

        level, reasons = decide(self.radar, self.cry, self.env)

        # 디바운스: 비정상이 연속 DEBOUNCE회 이상일 때만 확정
        self._streak = self._streak + 1 if level != "normal" else 0
        confirmed = level if (level == "normal" or self._streak >= DEBOUNCE) else "normal"
        show = reasons if confirmed != "normal" else []

        store.set_fusion(confirmed, show)
        bus.publish(topics.FUSION_STATE, {"level": confirmed, "reasons": show, "ts": topics.now()})

        # 상태 전이 + 쿨다운: 동일 경보 반복 로깅 억제
        if confirmed in ("attention", "alert") and confirmed != self.confirmed:
            now = topics.now()
            if now - self._last_alert_ts >= COOLDOWN_S:
                store.log(f"[{confirmed.upper()}] " + ", ".join(show))
                bus.publish(topics.ALERT, {"level": confirmed, "reason": ", ".join(show), "ts": topics.now()})
                self._last_alert_ts = now
        self.confirmed = confirmed
