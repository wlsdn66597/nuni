#!/usr/bin/env bash
# 소프트웨어적으로 가능한 것을 전부 실행하고 결과를 results/ 에 정리한다.
# 사용법 (리눅스):  bash run_all.sh
set -e
cd "$(dirname "$0")"
mkdir -p results

echo "[1/5] 멀티모달 융합 vs 단일센서 평가 (+ablation)"
python eval_fusion.py | tee results/eval_fusion.txt

echo "[2/5] 호흡 추정 DSP 검증 (MAE)"
python eval_radar.py | tee results/eval_radar.txt

DATA="cry_model/data"
if [ -d "$DATA" ] && [ -n "$(ls -A "$DATA" 2>/dev/null)" ]; then
  echo "[3/5] 울음 분류 학습"
  python cry_model/train.py "$DATA" --aug 2 | tee results/train.txt
  echo "[4/5] held-out 재평가"
  python cry_model/evaluate.py "$DATA" | tee results/evaluate.txt
  [ -f cry_model/artifacts/confusion_matrix.png ] && cp cry_model/artifacts/confusion_matrix.png results/
else
  echo "[skip] $DATA 없음 → 먼저: python cry_model/download_data.py cry" | tee results/train.txt
fi

echo "[5/5] RESULTS.md 생성"
{
  echo "# 실행 결과 (자동 생성)"
  echo
  echo "- 생성 시각: $(date)"
  echo
  echo "## 1. 멀티모달 융합 vs 단일 센서 (+ 모달리티 기여도)"
  echo '```'
  cat results/eval_fusion.txt
  echo '```'
  echo
  echo "## 2. 호흡 추정 DSP 검증 (설정 BPM = GT)"
  echo '```'
  cat results/eval_radar.txt
  echo '```'
  echo
  echo "## 3. 울음 분류 학습 (요약)"
  echo '```'
  tail -n 30 results/train.txt 2>/dev/null || echo "(미실행)"
  echo '```'
  echo
  echo "## 4. held-out 재평가"
  echo '```'
  cat results/evaluate.txt 2>/dev/null || echo "(미실행)"
  echo '```'
  echo
  echo "## 5. 혼동행렬"
  echo "![confusion matrix](confusion_matrix.png)"
  echo
  echo "## 6. 수동 수집 (자동화 불가)"
  echo "- 대시보드 스크린샷: \`streamlit run app.py\` 실행 후 캡처"
  echo "- E2E 지연: 대시보드에서 이벤트 발생 → 알림까지 시간"
} > results/RESULTS.md

echo "완료 → results/RESULTS.md"
