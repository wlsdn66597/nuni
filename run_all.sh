#!/usr/bin/env bash
set -euo pipefail

mkdir -p results/logs results/artifacts

echo "[1/5] compileall"
python -m compileall . | tee results/logs/compileall.log

echo "[2/5] radar synthetic DSP evaluation"
python eval_radar.py | tee results/logs/eval_radar.log

echo "[3/5] fusion controlled scenario evaluation"
python eval_fusion.py | tee results/logs/eval_fusion.log

echo "[4/5] dashboard/import smoke"
python - <<'PY' | tee results/logs/dashboard_import_smoke.log
mods = ["streamlit", "topics", "bus", "sim_sensors", "fusion", "workers", "state_store"]
for mod in mods:
    __import__(mod)
    print(f"[OK] import {mod}")
PY

echo "[5/5] write summary"
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
mae = radar_summary[0]["value"]
full = next(r for r in fusion_summary if r["policy"] == "full_fusion")
single = next(r for r in fusion_summary if r["policy"] == "single_sensor")
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
    f"| Single baseline | false alarm {single['false_alarm']}, miss {single['miss']} | `results/artifacts/fusion_ablation_summary.csv` |",
    "| Dashboard | import smoke success | `results/logs/dashboard_import_smoke.log` |",
    "| Cry ML | existing reports summarize limited reason-classifier performance | `reports/FINAL_CRY_MODEL_DECISION.md` |",
    "",
    "## Limits",
    "",
    "- Radar DSP is evaluated only on synthetic raw radar-like signals.",
    "- This run does not validate real 60GHz radar hardware.",
    "- Cry detection results in reports use synthetic negative audio for smoke testing.",
    "- Donate-a-Cry 5-class reason classification remains limited by class imbalance.",
]
(results / "RESULTS.md").write_text("\n".join(lines) + "\n")
print("wrote results/RESULTS.md")
PY

echo "run_all complete"
