#!/usr/bin/env python3
"""
Local FastMCP Server for Retail Pulse (Lab 3 Starter State).

Exposes Retail SQLite DB & POS/WMS/EDI Telemetry tools to Google Antigravity via MCP.
NOTE (Lab 3 Starter):
Only `query_true_atp_inventory` is implemented initially.
In Lab 3, you will implement the remaining 3 tools:
- `audit_vendor_otif_contracts`
- `simulate_promo_margin_guard`
- `list_at_risk_vip_orders`
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:
    from mcp.server.mcpserver import MCPServer as FastMCP

from src.services.inventory_atp import calculate_location_atp, get_sku_network_atp

mcp = FastMCP("retail-pulse-mcp")


@mcp.tool()
def query_true_atp_inventory(
    sku: str,
    location_id: str | None = None,
    required_qty: int = 1,
) -> dict[str, Any]:
    """
    Query True Available-to-Promise (ATP) inventory across WMS locations for a SKU,
    accounting for reserved_qty, safety_stock_qty, and unprocessed_webhook_delta_qty.
    """
    if location_id:
        res = calculate_location_atp(sku=sku, location_id=location_id, required_qty=required_qty)
        return {"sku": sku, "locations": [res.model_dump(mode="json")]}
    net = get_sku_network_atp(sku=sku, required_qty=required_qty)
    return {"sku": sku, "locations": [r.model_dump(mode="json") for r in net]}


# TODO (Lab 3): Implement `audit_vendor_otif_contracts(only_breaching: bool = True)`
# TODO (Lab 3): Implement `simulate_promo_margin_guard(sku: str, qty: int = 1, promo_codes_csv: str = "")`
# TODO (Lab 3): Implement `list_at_risk_vip_orders(loyalty_tier: str = "DIAMOND")`


if __name__ == "__main__":
    mcp.run()
