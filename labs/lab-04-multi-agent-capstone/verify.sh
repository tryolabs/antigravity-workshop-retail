#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

echo "=================================================================="
echo " Verifying Lab 04 Capstone & Full Workshop Suite (Labs 01 - 04)"
echo "=================================================================="
./.venv/bin/pytest tests/ -v
echo "=================================================================="
echo " [PASS] All 4 Labs Verified 100%!"
echo "=================================================================="
