"""융합 vs 단일 센서 정책 비교 평가 (보고서용 결과 생성).

라벨된 시나리오에서 각 정책의 오탐(false alarm)/미탐(miss)을 계산한다.
실행: python eval_fusion.py
"""
from fusion import decide, single_sensor_decide

# (이름, radar, cry, env, 정답=경보여야 하는가)
SCENARIOS = [
    ("정상 수면",
     {"presence": True, "breathing_rate": 40, "movement": 0.1},
     {"is_crying": False, "confidence": 0.1},
     {"co2": 600, "temp": 22}, False),
    ("무호흡",
     {"presence": True, "breathing_rate": 3, "movement": 0.05},
     {"is_crying": False, "confidence": 0.1},
     {"co2": 600, "temp": 22}, True),
    ("울음+뒤척임",
     {"presence": True, "breathing_rate": 42, "movement": 0.7},
     {"is_crying": True, "cls": "discomfort", "confidence": 0.85},
     {"co2": 650, "temp": 22}, True),
    ("외부 소음 오검출",
     {"presence": True, "breathing_rate": 40, "movement": 0.1},
     {"is_crying": True, "cls": "hungry", "confidence": 0.62},
     {"co2": 600, "temp": 22}, False),
    ("일시적 큰 움직임",
     {"presence": True, "breathing_rate": 41, "movement": 0.8},
     {"is_crying": False, "confidence": 0.1},
     {"co2": 600, "temp": 22}, False),
    ("CO₂ 약간 상승",
     {"presence": True, "breathing_rate": 40, "movement": 0.1},
     {"is_crying": False, "confidence": 0.1},
     {"co2": 850, "temp": 22}, False),
    ("무호흡+울음",
     {"presence": True, "breathing_rate": 4, "movement": 0.2},
     {"is_crying": True, "cls": "discomfort", "confidence": 0.9},
     {"co2": 600, "temp": 22}, True),
    ("온도 이상만",
     {"presence": True, "breathing_rate": 40, "movement": 0.1},
     {"is_crying": False, "confidence": 0.1},
     {"co2": 600, "temp": 29}, False),
]


def evaluate(policy):
    fa = miss = 0
    for _, r, c, e, expected in SCENARIOS:
        level, _ = policy(r, c, e)
        pred = (level == "alert")
        if pred and not expected:
            fa += 1
        if expected and not pred:
            miss += 1
    return fa, miss


def main():
    print(f"{'시나리오':<16}{'정답':<8}{'단일센서':<12}{'융합':<10}")
    print("-" * 48)
    for name, r, c, e, expected in SCENARIOS:
        s, _ = single_sensor_decide(r, c, e)
        f, _ = decide(r, c, e)
        print(f"{name:<16}{('경보' if expected else '정상'):<8}{s:<12}{f:<10}")

    s_fa, s_miss = evaluate(single_sensor_decide)
    f_fa, f_miss = evaluate(decide)
    print("-" * 48)
    print(f"{'단일 센서':<16} 오탐 {s_fa}건 · 미탐 {s_miss}건")
    print(f"{'멀티모달 융합':<14} 오탐 {f_fa}건 · 미탐 {f_miss}건")


if __name__ == "__main__":
    main()
