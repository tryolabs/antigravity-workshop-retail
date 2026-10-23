#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  ./install.sh
fi

# Automatically apply Lab 01, Lab 02, and Lab 03 solutions first!
./labs/lab-01-margin-inventory-triage/apply_solution.sh
./labs/lab-02-rules-and-skills/apply_solution.sh
./labs/lab-03-mcp-and-hooks/apply_solution.sh

# Reset Lab 04 fulfillment_router.py to starter stub
cp "$LAB_DIR/starter/fulfillment_router.py" "$ROOT_DIR/src/services/fulfillment_router.py"

echo "=================================================================="
echo " [Lab 04 Ready] Multi-Agent Capstone: Omnichannel Routing & Chargebacks"
echo " -> Prerequisite Lab 01, Lab 02 & Lab 03 solutions automatically applied."
echo " -> Guide (EN): labs/lab-04-multi-agent-capstone/README.md"
echo " -> Guide (ES): labs/lab-04-multi-agent-capstone/README.es.md"
echo " -> Prompts:    labs/lab-04-multi-agent-capstone/PROMPTS.md"
echo "=================================================================="
