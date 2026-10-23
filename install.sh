#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "=================================================================="
echo " Retail Pulse: Google Antigravity Retail Workshop Installer"
echo "=================================================================="

if [ ! -d ".venv" ]; then
  echo "[1/3] Creating Python virtual environment (.venv)..."
  if command -v uv >/dev/null 2>&1; then
    uv venv .venv
  else
    python3 -m venv .venv
  fi
else
  echo "[1/3] Using existing Python virtual environment (.venv)..."
fi

echo "[2/3] Checking / installing Python dependencies..."
if ./.venv/bin/python -c "import fastapi, uvicorn, pydantic, pytest, httpx, mcp, google.adk" >/dev/null 2>&1; then
  echo "      [OK] Pre-provisioned .venv detected with all required packages (zero-install mode)."
elif [ -d "wheelhouse" ]; then
  echo "      [Offline Mode] Installing from local ./wheelhouse..."
  ./.venv/bin/pip install --quiet --no-index --find-links ./wheelhouse -r requirements.txt
elif command -v uv >/dev/null 2>&1; then
  uv pip install --python ./.venv/bin/python -r requirements.txt
else
  ./.venv/bin/pip install --quiet -r requirements.txt
fi

echo "[3/3] Seeding deterministic Retail Pulse WMS, POS & OTIF SQLite database..."

./.venv/bin/python data/seed_retail_data.py

echo ""
echo "[OK] Retail Pulse environment ready!"
echo " -> Run Web Dashboard: ./.venv/bin/uvicorn src.main:app --reload --port 8002"
echo " -> Start Lab 1:       ./labs/lab-01-margin-inventory-triage/install.sh"
