#!/usr/bin/env bash
set -euo pipefail

LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$LAB_DIR/../.." && pwd)"
cd "$ROOT_DIR"

cp "$LAB_DIR/solution/promo_pricing.py" "$ROOT_DIR/src/services/promo_pricing.py"
cp "$LAB_DIR/solution/inventory_atp.py" "$ROOT_DIR/src/services/inventory_atp.py"

echo "[OK] Applied Lab 01 Reference Solution (promo_pricing.py & inventory_atp.py)."
