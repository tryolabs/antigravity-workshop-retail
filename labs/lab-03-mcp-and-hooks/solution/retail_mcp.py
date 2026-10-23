#!/usr/bin/env python3
"""
Local FastMCP Server for Retail Pulse (Lab 3 Reference Solution).

Exposes 4 domain-specific Retail Omnichannel & Commercial Intelligence tools over MCP:
1. `query_true_atp_inventory`
2. `audit_vendor_otif_contracts`
3. `simulate_promo_margin_guard`
4. `list_at_risk_vip_orders`
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

from src.services.inventory_atp import (
    audit_vip_oversell_exposure,
    calculate_location_atp,
    get_sku_network_atp,
)
from src.services.promo_pricing import evaluate_order_line_pricing
from src.services.vendor_otif_auditor import audit_vendor_contracts

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


@mcp.tool()
def audit_vendor_otif_contracts(only_breaching: bool = True) -> dict[str, Any]:
    """
    Cross-reference supplier commercial OTIF contracts against EDI 856 ASN delay/shortage
    telemetry logs and calculate recoverable vendor chargeback penalties in USD.
    """
    return audit_vendor_contracts(only_breaching=only_breaching)


@mcp.tool()
def simulate_promo_margin_guard(
    sku: str,
    qty: int = 1,
    promo_codes_csv: str = "",
) -> dict[str, Any]:
    """
    Simulate promotional discount stacking and commercial margin floor clamping for a SKU
    quantity and comma-separated promo codes list (e.g. 'VIP25,FLASH20').
    """
    codes = [c.strip() for c in promo_codes_csv.split(",") if c.strip()]
    res = evaluate_order_line_pricing(sku=sku, qty=qty, promo_codes=codes)
    return res.model_dump(mode="json")


@mcp.tool()
def list_at_risk_vip_orders(loyalty_tier: str = "DIAMOND") -> dict[str, Any]:
    """
    List AT_RISK_STOCKOUT omnichannel orders filtered by loyalty tier (e.g. 'DIAMOND' or 'GOLD')
    where POS webhook sync lag or safety stock buffers create phantom-stock oversell risk.
    """
    exposure = audit_vip_oversell_exposure()
    tier_upper = loyalty_tier.strip().upper()
    filtered = [
        o for o in exposure["flagged_orders"]
        if tier_upper in ("ALL", "*") or str(o["loyalty_tier"]).upper() == tier_upper
    ]
    exposed_ltv = round(sum(float(o["customer_ltv_usd"]) for o in filtered), 2)
    return {
        "requested_loyalty_tier": tier_upper,
        "matching_at_risk_orders_count": len(filtered),
        "exposed_customer_ltv_usd": exposed_ltv,
        "orders": filtered,
    }


if __name__ == "__main__":
    mcp.run()
