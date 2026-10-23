#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  ./install.sh
fi

# Reset codebase to Lab 1 Starter state (with Bug #1A and Bug #1B active)
cp "$LAB_DIR/starter/promo_pricing.py" "$ROOT_DIR/src/services/promo_pricing.py"
cp "$LAB_DIR/starter/inventory_atp.py" "$ROOT_DIR/src/services/inventory_atp.py"
cp "$ROOT_DIR/labs/lab-03-mcp-and-hooks/starter/retail_mcp.py" "$ROOT_DIR/mcp_server/retail_mcp.py"
cp "$ROOT_DIR/labs/lab-04-multi-agent-capstone/starter/fulfillment_router.py" "$ROOT_DIR/src/services/fulfillment_router.py"
rm -f "$ROOT_DIR/GEMINI.md" \
      "$ROOT_DIR/.agents/rules/retail-standards.md" \
      "$ROOT_DIR/.agents/skills/margin-otif-audit/SKILL.md" \
      "$ROOT_DIR/.agents/mcp_config.json" \
      "$ROOT_DIR/.agents/hooks.json"

./.venv/bin/python data/seed_retail_data.py >/dev/null

echo "=================================================================="
echo " [Lab 01 Ready] Margin Floor & True ATP Inventory Triage"
echo " -> Intentional Bug #1A active in: src/services/promo_pricing.py"
echo " -> Intentional Bug #1B active in: src/services/inventory_atp.py"
echo " -> Guide (EN): labs/lab-01-margin-inventory-triage/README.md"
echo " -> Guide (ES): labs/lab-01-margin-inventory-triage/README.es.md"
echo " -> Prompts:    labs/lab-01-margin-inventory-triage/PROMPTS.md"
echo "=================================================================="
