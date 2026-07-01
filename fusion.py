"""멀티모달 융합 판단 엔진.

decide(): 레이더+음향+환경을 교차검증하는 규칙 (핵심 차별점)
single_sensor_decide(): 비교용 단일 센서 단순 정책 (오탐이 많음)
-> eval_fusion.py 에서 둘을 비교해 "융합이 오탐을 줄인다"를 정량화.
"""
import topics
import bus
from state_store import store
import time

_ORDER = {"normal": 0, "attention": 1, "alert": 2}


def _max(a, b):
    return a if _ORDER[a] >= _ORDER[b] else b


def decide(radar, cry, env):
    """(level, reasons) 반환. level: normal/attention/alert"""
    level, reasons = "normal", []

    apnea = bool(radar and radar.get("apnea"))
    br = radar.get("breathing_rate", radar.get("breathing_bpm", 99)) if radar else 99
    if radar and radar.get("presence") and (apnea or br < 8):
        level = _max(level, "alert")
        reasons.append("호흡 미검출·무호흡 의심")

    cry_conf = cry.get("confidence", cry.get("cry_score", 0)) if cry else 0
    cry_flag = bool(cry and cry.get("is_crying") and cry_conf >= 0.7)
    if cry_flag:
        level = _max(level, "attention")
        reasons.append(f"울음 감지({cry.get('cls')})")

    # 교차검증: 울음 + (호흡 이상 or 큰 움직임)이 동시일 때만 경보로 상향
    if cry_flag and radar and (radar.get("movement", 0) > 0.6 or apnea or br < 8):
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
    if radar and radar.get("apnea"):
        return "alert", ["무호흡(단일)"]
    if radar and radar.get("movement", 0) > 0.5:
        return "alert", ["움직임(단일)"]
    if env and env.get("co2", 0) > 800:
        return "alert", ["CO₂(단일)"]
    return "normal", []


class Fusion:
    """라이브 구독자: 최신 신호를 모아 판단하고 상태/경보를 발행."""

    def __init__(self, debounce_n=2, cooldown_s=10):
        self.radar = self.cry = self.env = None
        self.last = "normal"
        self.debounce_n = debounce_n
        self.cooldown_s = cooldown_s
        self._candidate = "normal"
        self._candidate_count = 0
        self._last_alert_key = None
        self._last_alert_ts = 0.0

    def _debounce(self, level):
        if level == "normal":
            self._candidate = "normal"
            self._candidate_count = 0
            return level
        if level == self._candidate:
            self._candidate_count += 1
        else:
            self._candidate = level
            self._candidate_count = 1
        return level if self._candidate_count >= self.debounce_n else "normal"

    def _cooldown_allows(self, level, reasons):
        key = (level, "|".join(reasons))
        now = time.time()
        if key == self._last_alert_key and now - self._last_alert_ts < self.cooldown_s:
            return False
        self._last_alert_key = key
        self._last_alert_ts = now
        return True

    def on_message(self, topic, payload):
        if topic == topics.RADAR:
            self.radar = payload
        elif topic == topics.CRY:
            self.cry = payload
        elif topic == topics.ENV:
            self.env = payload

        raw_level, reasons = decide(self.radar, self.cry, self.env)
        level = self._debounce(raw_level)
        out_reasons = reasons if level != "normal" else []
        store.set_fusion(level, out_reasons)
        bus.publish(topics.FUSION_STATE, {"level": level, "reasons": out_reasons, "raw_level": raw_level, "ts": topics.now()})

        if level != "normal" and level != self.last and self._cooldown_allows(level, out_reasons):
            store.log(f"[{level.upper()}] " + ", ".join(out_reasons))
            bus.publish(topics.ALERT, {"level": level, "reason": ", ".join(out_reasons), "ts": topics.now()})
        self.last = level
