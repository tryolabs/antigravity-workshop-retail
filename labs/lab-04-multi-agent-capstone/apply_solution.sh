#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

cp "$LAB_DIR/solution/fulfillment_router.py" "$ROOT_DIR/src/services/fulfillment_router.py"
cp "$LAB_DIR/solution/main.py" "$ROOT_DIR/src/main.py"

echo "[OK] Applied Lab 04 Reference Solution (fulfillment_router.py & main.py)."
