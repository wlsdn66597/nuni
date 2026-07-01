#!/usr/bin/env bash
set -euo pipefail

mkdir -p results/logs results/artifacts

echo "[1/8] compileall"
python -m compileall . | tee results/logs/compileall.log

echo "[2/8] radar synthetic DSP evaluation"
python eval_radar.py | tee results/logs/eval_radar.log

echo "[3/8] fusion controlled scenario evaluation"
python eval_fusion.py | tee results/logs/eval_fusion.log

echo "[4/8] streaming fusion evaluation (debounce/cooldown)"
python eval_stream.py | tee results/logs/eval_stream.log

echo "[5/8] voice intent evaluation"
python voice_intent.py | tee results/logs/voice_intent.log

echo "[6/8] cloud sleep report"
python cloud.py | tee results/logs/cloud.log

echo "[7/8] dashboard/import smoke"
python - <<'PY' | tee results/logs/dashboard_import_smoke.log
mods = ["streamlit", "topics", "bus", "sim_sensors", "fusion", "workers", "state_store"]
for mod in mods:
    __import__(mod)
    print(f"[OK] import {mod}")
PY

echo "[8/8] write summary"
python - <<'PY'
import csv
import subprocess
import sys
from datetime import datetime
from pathlib import Path

results = Path("results")
art = results / "artifacts"

def read_summary_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))

radar_summary = read_summary_csv(art / "radar_bpm_error_summary.csv")
fusion_summary = read_summary_csv(art / "fusion_ablation_summary.csv")
stream_summary = read_summary_csv(art / "stream_eval_summary.csv")
mae = radar_summary[0]["value"]
full = next(r for r in fusion_summary if r["policy"] == "full_fusion")
single = next(r for r in fusion_summary if r["policy"] == "single_sensor")
radar_only = next(r for r in fusion_summary if r["policy"] == "radar_only")
raw = next(r for r in stream_summary if r["debounce_n"] == "1")
tuned = next(r for r in stream_summary if r["debounce_n"] == "2")
commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
pyver = sys.version.split()[0]

lines = [
    "# NUNI Software Verification Results",
    "",
    "## Environment",
    "",
    f"- Python: {pyver}",
    f"- Git commit: `{commit}`",
    f"- Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    "",
    "## Summary",
    "",
    "| Area | Result | Artifact |",
    "|---|---|---|",
    "| Basic validation | compileall success | `results/logs/compileall.log` |",
    f"| Radar DSP | synthetic BPM MAE {mae} breaths/min | `results/RADAR_DSP_RESULT.md` |",
    f"| Fusion | full fusion false alarm {full['false_alarm']}, miss {full['miss']} | `results/FUSION_EVALUATION_RESULT.md` |",
    f"| Fusion vs radar-only | radar-only miss {radar_only['miss']} (fusion catches) | `results/artifacts/fusion_ablation_summary.csv` |",
    f"| Single baseline | false alarm {single['false_alarm']}, miss {single['miss']} | `results/artifacts/fusion_ablation_summary.csv` |",
    f"| Streaming (debounce/cooldown) | alerts {raw['total_alerts']}->{tuned['total_alerts']}, apnea latency {tuned['apnea_detect_latency_s']}s | `results/STREAM_EVAL_RESULT.md` |",
    "| Voice intent | keyword intent recognition | `results/VOICE_INTENT_RESULT.md` |",
    "| Cloud sleep report | overnight summary generated | `results/SLEEP_REPORT.md` |",
    "| Dashboard | import smoke success | `results/logs/dashboard_import_smoke.log` |",
    "| Cry ML | limited reason-classifier (class imbalance) | `results/CRY_CLASSIFICATION_LIMITATION.md` |",
    "",
    "## Limits",
    "",
    "- Radar DSP is evaluated only on synthetic raw radar-like signals.",
    "- Streaming/fusion results use controlled synthetic timelines, not real sensors.",
    "- Voice intent accuracy is on a curated phrase set; real STT/noise will differ.",
    "- Cloud sleep report uses a synthetic night, not real infant data.",
    "- Donate-a-Cry 5-class reason classification remains limited by class imbalance.",
]
(results / "RESULTS.md").write_text("\n".join(lines) + "\n")
print("wrote results/RESULTS.md")
PY

echo "run_all complete"
