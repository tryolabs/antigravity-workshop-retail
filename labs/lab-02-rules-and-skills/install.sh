#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  ./install.sh
fi

# Automatically apply Lab 01 solution first so latecomers are caught up!
./labs/lab-01-margin-inventory-triage/apply_solution.sh

# Clean Lab 02 target files so attendee starts Lab 02 fresh
rm -f "$ROOT_DIR/GEMINI.md" \
      "$ROOT_DIR/.agents/rules/retail-standards.md" \
      "$ROOT_DIR/.agents/skills/margin-otif-audit/SKILL.md" \
      "$ROOT_DIR/data/exports/executive_margin_otif_audit.json" \
      "$ROOT_DIR/data/exports/executive_margin_otif_audit.md"

echo "=================================================================="
echo " [Lab 02 Ready] Workspace Rules (GEMINI.md) & Skills (SKILL.md)"
echo " -> Prerequisite Lab 01 solution automatically applied."
echo " -> Guide (EN): labs/lab-02-rules-and-skills/README.md"
echo " -> Guide (ES): labs/lab-02-rules-and-skills/README.es.md"
echo " -> Prompts:    labs/lab-02-rules-and-skills/PROMPTS.md"
echo "=================================================================="
