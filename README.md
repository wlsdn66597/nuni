# NUNI — 비접촉 영유아 케어 AI (소프트웨어)

레이더·음향·환경 센서로 **카메라·웨어러블 없이** 영유아의 호흡·움직임·울음을 해석하고,
이상 징후를 선제적으로 알리는 AI 시스템의 **소프트웨어 파이프라인**.

> **대회**: 2026 AI소프트웨어공모전 (임베디드SW 트랙) — 1차 결과보고서 + 2차 데모 심사
> **현재 단계**: 소프트웨어 구현 완료(시뮬레이션·공개데이터 검증) / 실물 센서 통합은 2차 데모까지

---

## 1. 프로젝트 개요

- **문제**: 부모는 영유아 상태를 계속 확인해야 하는 불안·수면부족을 겪는다. 기존 제품은 웨어러블 착용·카메라 사용이라 프라이버시·거부감 문제가 있다.
- **해결**: 60GHz 레이더(호흡·움직임)·마이크(울음·음성)·환경센서(온습도·CO₂·조도)를 **멀티모달 융합**해, 카메라 없이 상태를 해석하고 선제 알림/제어한다.
- **핵심 차별점**: ①비접촉·비영상 ②멀티모달 융합으로 단일센서 오탐 감소 ③엣지 처리로 프라이버시 보호.

## 2. 시스템 구조

```
[센서/음성 입력]  ──(MQTT 토픽)──▶  [엣지 AI 추론]  ──▶  [멀티모달 융합]  ──▶  [대시보드·알림]
 레이더/환경(가상·실물)              울음분류(YAMNet)        시간동기·교차검증
 마이크                             음성 인텐트             위험도·불편 판단
```
모든 모듈은 MQTT 토픽으로만 통신 → **가상 센서를 실물로 무중단 교체 가능**. (토픽 규격은 §부록)

## 3. 구현 상태

| 구분 | 항목 |
|---|---|
| **완료 (소프트웨어)** | MQTT 아키텍처 · 멀티모달 융합 엔진 · 울음 분류(YAMNet 전이학습) · 대시보드 · 알림 · 평가 프레임워크 |
| **2차 데모까지 예정** | 실물 60GHz 레이더·환경센서 통합 · 원거리 마이크 실수음 · 실환경 재검증 |

## 4. 저장소 구성

```
nuni_demo/
├─ topics.py            # MQTT 토픽 규격(이름 + 메시지 스키마)
├─ bus.py               # pub/sub 추상화 (inproc 기본 / mqtt 선택)
├─ sim_sensors.py       # 레이더·환경 가상 발행자  ← 실물 교체 지점
├─ cry_classifier.py    # 울음 분류 (시뮬 기본 / REAL=True 시 YAMNet)
├─ fusion.py            # 멀티모달 융합 판단 + 단일센서 비교 정책
├─ workers.py           # inproc 백그라운드 워커 기동
├─ app.py               # Streamlit 실시간 대시보드
├─ eval_fusion.py       # 융합 vs 단일센서 오탐/미탐 평가
├─ requirements.txt     # 데모 실행 의존성
└─ cry_model/           # 울음 분류 학습 파이프라인
   ├─ config.py         # 경로·하이퍼파라미터
   ├─ features.py       # YAMNet 로드 + 임베딩/울음감지(+캐시)
   ├─ augment.py        # 잔향·소음·거리 증강 (실측 파일 or 합성)
   ├─ prepare_data.py   # 데이터 인덱싱(화자 group 분리)
   ├─ train.py          # 전이학습 + held-out 평가 + 혼동행렬
   ├─ evaluate.py       # 저장 모델 재평가
   ├─ infer.py          # 마이크/파일 추론
   ├─ check_env.py      # 학습 전 환경 점검
   ├─ download_data.py  # 데이터 자동 다운로드
   └─ requirements-ml.txt
```

## 5. 데모 실행 (하드웨어 불필요)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py          # 대시보드 (사이드바로 울음/무호흡 주입)
python eval_fusion.py         # 융합 성능 비교표
```

## 6. 울음 분류 학습 (핵심 AI)

```bash
source .venv/bin/activate
pip install -r cry_model/requirements-ml.txt

python cry_model/download_data.py cry     # Donate-a-Cry → cry_model/data/
python cry_model/download_data.py noise   # (선택) ESC-50 → cry_model/noise/
python cry_model/check_env.py             # 라이브러리·YAMNet·데이터 점검
python cry_model/prepare_data.py cry_model/data   # 클래스 분포 확인
python cry_model/train.py cry_model/data --aug 2  # 학습 → cry_model/artifacts/
python cry_model/evaluate.py cry_model/data       # held-out 재평가
```
학습 후 데모에 연결: `cry_classifier.py`에서 `REAL = True`.

## 7. 필요한 데이터셋

| 데이터 | 용도 | 출처 |
|---|---|---|
| Donate-a-Cry Corpus | 울음 이유 분류 학습(필수) | github.com/gveres/donateacry-corpus |
| Infant Cry Audio Corpus | 표본 보강(권장) | Kaggle |
| ESC-50 | 증강 소음 + 감지 오탐 검증 | github.com/karoldvl/ESC-50 |
| MUSAN / RIR(OpenAIR 등) | 실측 소음·잔향 증강 | openslr.org/17 |
| YAMNet | 사전학습 백본(자동 로드) | TF Hub |

> ⚠️ Donate-a-Cry는 표본이 적고 불균형 → 증강·class_weight·전이학습으로 보완, rare 클래스는 합쳐 거친 카테고리로.

## 8. 받아와야 할 결과물 (보고서용)

| 산출물 | 생성 방법 | 보고서 위치 |
|---|---|---|
| **융합 vs 단일 오탐/미탐 표** | `python eval_fusion.py` | 구현기능 — 융합 효과 |
| **혼동행렬 이미지** | `train.py` → `cry_model/artifacts/confusion_matrix.png` | 구현기능 — 울음 분류 |
| **Macro-F1 / 클래스별 성능** | `train.py`·`evaluate.py` 출력 | 구현기능 — 울음 분류 |
| **대시보드 스크린샷** | `streamlit run app.py` 실행 화면 | 작품 사진 / 구현기능 |
| **E2E 지연 측정** | 이벤트→알림 타임스탬프 | 검증 방법 및 결과 |

## 9. 실물 교체 지점 (2차 데모까지)

1. **센서**: `sim_sensors.py`의 `radar_step()/env_step()`를 실물 UART/I2C 읽기로 교체 (토픽 동일)
2. **울음**: `cry_classifier.py` `REAL=True` + 학습된 `artifacts/` 사용
3. **분산 실행**: `NUNI_BUS=mqtt` + 로컬 Mosquitto → 각 모듈 별도 프로세스

## 10. 검증 방법 & 정직성

- 울음/음성: **공개 데이터 라벨 = GT**, 화자단위 held-out.
- 레이더/환경: **시뮬레이션·공개데이터로 검증**(코드에 시뮬 명시), 실물 재검증은 2차.
- 융합: **통제된 시나리오 정답과 비교**(`eval_fusion.py`).
- 본 검증은 실제 영유아 임상검증이 아니며, 제품화 시 IRB·임상이 필요하다.

---

## 부록 — MQTT 토픽 규격

| 토픽 | 페이로드 |
|---|---|
| `sensor/radar` | `{breathing_rate, movement(0~1), presence, ts}` |
| `sensor/env` | `{temp, humidity, co2, lux, ts}` |
| `audio/cry` | `{is_crying, cls, confidence, ts}` |
| `audio/voice` | `{intent, ts}` |
| `fusion/state` | `{level(normal/attention/alert), reasons[], ts}` |
| `fusion/alert` | `{level, reason, ts}` |
