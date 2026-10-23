#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d ".venv" ]; then
  ./install.sh
fi

# Automatically apply Lab 01 and Lab 02 solutions first!
./labs/lab-01-margin-inventory-triage/apply_solution.sh
./labs/lab-02-rules-and-skills/apply_solution.sh

# Reset Lab 03 files to starter state
cp "$LAB_DIR/starter/retail_mcp.py" "$ROOT_DIR/mcp_server/retail_mcp.py"
rm -f "$ROOT_DIR/.agents/mcp_config.json" "$ROOT_DIR/.agents/hooks.json"

echo "=================================================================="
echo " [Lab 03 Ready] FastMCP Retail Server & PreToolUse Margin Guard Hooks"
echo " -> Prerequisite Lab 01 & Lab 02 solutions automatically applied."
echo " -> Guide (EN): labs/lab-03-mcp-and-hooks/README.md"
echo " -> Guide (ES): labs/lab-03-mcp-and-hooks/README.es.md"
echo " -> Prompts:    labs/lab-03-mcp-and-hooks/PROMPTS.md"
echo "=================================================================="
