#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "=================================================================="
echo " Retail Pulse: Google Antigravity Retail Workshop Installer"
echo "=================================================================="

if [ ! -d ".venv" ]; then
  if command -v uv >/dev/null 2>&1; then
    uv venv .venv
  else
    python3 -m venv .venv
  fi
fi

if command -v uv >/dev/null 2>&1; then
  uv pip install -r requirements.txt
else
  ./.venv/bin/pip install --quiet -r requirements.txt
fi

./.venv/bin/python data/seed_retail_data.py

echo ""
echo "[OK] Retail Pulse environment ready!"
echo " -> Run Web Dashboard: ./.venv/bin/uvicorn src.main:app --reload --port 8002"
echo " -> Start Lab 1:       ./labs/lab-01-margin-inventory-triage/install.sh"
