#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

echo "=================================================================="
echo " Verifying Lab 03: FastMCP Tools, mcp_config.json & Guard Hooks"
echo "=================================================================="
./.venv/bin/pytest tests/test_lab01_triage.py tests/test_lab02_rules_skills.py tests/test_lab03_mcp_hooks.py -v
echo "=================================================================="
echo " [PASS] Lab 03 Verification Complete (100%)"
echo "=================================================================="
