#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

mkdir -p "$ROOT_DIR/.agents/rules" "$ROOT_DIR/.agents/skills/margin-otif-audit"
cp "$LAB_DIR/solution/GEMINI.md" "$ROOT_DIR/GEMINI.md"
cp "$LAB_DIR/solution/retail-standards.md" "$ROOT_DIR/.agents/rules/retail-standards.md"
cp "$LAB_DIR/solution/SKILL.md" "$ROOT_DIR/.agents/skills/margin-otif-audit/SKILL.md"
./.venv/bin/python scripts/run_otif_margin_audit.py >/dev/null

echo "[OK] Applied Lab 02 Reference Solution (GEMINI.md, retail-standards.md, margin-otif-audit/SKILL.md)."
