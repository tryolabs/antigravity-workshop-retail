#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

echo "=================================================================="
echo " Verifying Lab 01: Promo Margin Floor & True ATP Inventory Triage"
echo "=================================================================="
./.venv/bin/pytest tests/test_lab01_triage.py -v
echo "=================================================================="
echo " [PASS] Lab 01 Verification Complete (100%)"
echo "=================================================================="
