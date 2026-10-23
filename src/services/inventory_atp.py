"""
Available-to-Promise (ATP) & POS Webhook Drift Calculator.

NOTE (Lab 1 Starter State):
This service currently contains intentional Lab 1 Bug #1B:
It calculates `true_atp_qty` simply as `on_hand_qty`, completely ignoring:
- `reserved_qty` (orders already allocated in WMS)
- `safety_stock_qty` (buffer inventory floor)
- `unprocessed_webhook_delta_qty` (in-store POS checkouts lagging behind webhook sync)

This causes severe phantom-stock overselling on VIP (`DIAMOND` / `GOLD`) high-LTV orders!
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from src.database import fetch_all, fetch_one
from src.models import ATPCalculationResult


def _q2(val: float | int | str | Decimal) -> Decimal:
    return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_location_atp(
    sku: str,
    location_id: str,
    required_qty: int = 1,
    db_path: Path | None = None,
) -> ATPCalculationResult:
    """
    Calculate Available-to-Promise (ATP) for a SKU at a specific fulfillment location.
    (Lab 1 Starter Version — Contains Bug #1B)
    """
    row = fetch_one(
        "SELECT * FROM wms_inventory WHERE sku = ? AND location_id = ?",
        (sku, location_id),
        db_path=db_path,
    )
    if not row:
        raise ValueError(f"Inventory record not found for SKU={sku} at location={location_id}")

    on_hand = int(row["on_hand_qty"])
    reserved = int(row["reserved_qty"])
    safety_stock = int(row["safety_stock_qty"])
    webhook_delta = int(row["unprocessed_webhook_delta_qty"])

    # BUG 1B: Returns on_hand_qty directly without subtracting reserved_qty,
    # safety_stock_qty, and unprocessed_webhook_delta_qty!
    raw_atp = on_hand
    true_atp = on_hand
    oversell_risk = False

    return ATPCalculationResult(
        inventory_id=row["inventory_id"],
        location_id=row["location_id"],
        location_type=row["location_type"],
        sku=row["sku"],
        gtin_14=row["gtin_14"],
        product_name=row["product_name"],
        category=row["category"],
        on_hand_qty=on_hand,
        reserved_qty=reserved,
        safety_stock_qty=safety_stock,
        unprocessed_webhook_delta_qty=webhook_delta,
        raw_atp_qty=raw_atp,
        true_atp_qty=true_atp,
        oversell_risk=oversell_risk,
        shipping_cost_usd=_q2(row["shipping_cost_usd"]),
    )


def get_sku_network_atp(
    sku: str,
    required_qty: int = 1,
    db_path: Path | None = None,
) -> list[ATPCalculationResult]:
    """Return ATP calculation across all 6 fulfillment locations for a SKU."""
    rows = fetch_all(
        "SELECT location_id FROM wms_inventory WHERE sku = ? ORDER BY location_id",
        (sku,),
        db_path=db_path,
    )
    return [
        calculate_location_atp(sku=sku, location_id=r["location_id"], required_qty=required_qty, db_path=db_path)
        for r in rows
    ]


def audit_vip_oversell_exposure(db_path: Path | None = None) -> dict[str, Any]:
    """
    Audit AT_RISK_STOCKOUT orders for DIAMOND & GOLD loyalty tiers and evaluate whether
    their assigned fulfillment location actually has sufficient True ATP.
    """
    orders = fetch_all(
        """
        SELECT * FROM omnichannel_orders
        WHERE order_status = 'AT_RISK_STOCKOUT'
        ORDER BY customer_ltv_usd DESC
        """,
        db_path=db_path,
    )
    flagged_orders: list[dict[str, Any]] = []
    exposed_ltv_usd = Decimal("0.00")

    for o in orders:
        atp_res = calculate_location_atp(
            sku=o["sku"],
            location_id=o["fulfillment_location_id"],
            required_qty=int(o["qty"]),
            db_path=db_path,
        )
        if atp_res.oversell_risk or atp_res.true_atp_qty < int(o["qty"]):
            exposed_ltv_usd += _q2(o["customer_ltv_usd"])
            flagged_orders.append(
                {
                    "order_id": o["order_id"],
                    "customer_id": o["customer_id"],
                    "loyalty_tier": o["loyalty_tier"],
                    "customer_ltv_usd": float(o["customer_ltv_usd"]),
                    "sku": o["sku"],
                    "qty": int(o["qty"]),
                    "fulfillment_location_id": o["fulfillment_location_id"],
                    "on_hand_qty": atp_res.on_hand_qty,
                    "true_atp_qty": atp_res.true_atp_qty,
                    "oversell_risk": atp_res.oversell_risk,
                }
            )

    return {
        "at_risk_orders_total": len(orders),
        "detected_oversell_orders_count": len(flagged_orders),
        "exposed_customer_ltv_usd": float(exposed_ltv_usd),
        "flagged_orders": flagged_orders,
    }
