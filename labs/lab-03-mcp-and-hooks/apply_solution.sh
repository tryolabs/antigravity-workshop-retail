#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

mkdir -p "$ROOT_DIR/.agents"
cp "$LAB_DIR/solution/retail_mcp.py" "$ROOT_DIR/mcp_server/retail_mcp.py"
cp "$LAB_DIR/solution/mcp_config.json" "$ROOT_DIR/.agents/mcp_config.json"
cp "$LAB_DIR/solution/hooks.json" "$ROOT_DIR/.agents/hooks.json"

echo "[OK] Applied Lab 03 Reference Solution (retail_mcp.py, mcp_config.json, hooks.json)."
