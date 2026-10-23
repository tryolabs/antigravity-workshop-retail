"""
Promotional Pricing & Commercial Margin Floor Engine.

NOTE (Lab 1 Starter State):
This service currently contains intentional Lab 1 Bug #1A:
1. It allows non-stackable promo codes (and even inactive codes) to stack together.
2. It sums discount percentages additively (e.g., 25% + 20% + 30% = 75% off!) instead of
   selecting the best non-stackable promo or compounding stackable promos.
3. It uses binary float math instead of Decimal(ROUND_HALF_UP) and completely ignores
   `contract_min_margin_floor_pct`, selling flagship SKUs below wholesale cost!
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from src.database import fetch_all, fetch_one
from src.models import PromoEvaluationResult


def _to_dec(val: float | int | str | Decimal) -> Decimal:
    return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def evaluate_order_line_pricing(
    sku: str,
    qty: int = 1,
    promo_codes: list[str] | None = None,
    db_path: Path | None = None,
) -> PromoEvaluationResult:
    """
    Evaluate promotional discounts and commercial margin for a SKU order line.
    (Lab 1 Starter Version — Contains Bug #1A)
    """
    if qty < 1:
        raise ValueError("Order quantity must be >= 1")

    sku_row = fetch_one(
        "SELECT * FROM sku_catalog WHERE sku = ?",
        (sku,),
        db_path=db_path,
    )
    if not sku_row:
        raise ValueError(f"Unknown SKU: {sku}")

    requested_codes = [c.strip().upper() for c in (promo_codes or []) if c and c.strip()]

    unit_price = float(sku_row["unit_price_usd"])
    unit_cost = float(sku_row["unit_wholesale_cost_usd"])
    contract_floor_pct = float(sku_row["contract_min_margin_floor_pct"])

    gross_revenue = unit_price * qty
    total_wholesale_cost = unit_cost * qty

    # BUG 1A: Naive additive stacking of all promo codes without checking
    # active flag, is_stackable flag, or contract_min_margin_floor_pct!
    total_discount_pct = 0.0
    applied_codes: list[str] = []
    rejected_codes: list[str] = []

    for code in requested_codes:
        promo_row = fetch_one(
            "SELECT * FROM promo_campaigns WHERE promo_code = ?",
            (code,),
            db_path=db_path,
        )
        if promo_row:
            total_discount_pct += float(promo_row["discount_pct"])
            applied_codes.append(code)
        else:
            rejected_codes.append(code)

    discount_amount = round(gross_revenue * (total_discount_pct / 100.0), 2)
    net_revenue = round(gross_revenue - discount_amount, 2)
    gross_margin_usd = round(net_revenue - total_wholesale_cost, 2)
    gross_margin_pct = round((gross_margin_usd / net_revenue) * 100.0, 2) if net_revenue > 0 else -100.0

    return PromoEvaluationResult(
        sku=sku_row["sku"],
        gtin_14=sku_row["gtin_14"],
        qty=qty,
        unit_price_usd=_to_dec(unit_price),
        unit_wholesale_cost_usd=_to_dec(unit_cost),
        contract_min_margin_floor_pct=_to_dec(contract_floor_pct),
        requested_promo_codes=requested_codes,
        applied_promo_codes=applied_codes,
        rejected_promo_codes=rejected_codes,
        gross_revenue_usd=_to_dec(gross_revenue),
        discount_amount_usd=_to_dec(discount_amount),
        net_revenue_usd=_to_dec(net_revenue),
        total_wholesale_cost_usd=_to_dec(total_wholesale_cost),
        gross_margin_usd=_to_dec(gross_margin_usd),
        gross_margin_pct=_to_dec(gross_margin_pct),
        margin_floor_clamped=False,
        margin_compliant=True,  # Buggy engine claims everything is compliant!
    )


def audit_margin_hold_orders(db_path: Path | None = None) -> dict[str, Any]:
    """
    Scan all MARGIN_HOLD orders in omnichannel_orders and compare legacy recorded
    margins against the current promo pricing engine.
    """
    orders = fetch_all(
        "SELECT * FROM omnichannel_orders WHERE order_status = 'MARGIN_HOLD' ORDER BY order_id",
        db_path=db_path,
    )
    legacy_negative_leakage_usd = Decimal("0.00")
    recalculated_margin_usd = Decimal("0.00")
    protected_orders_count = 0

    for row in orders:
        legacy_margin = _to_dec(row["gross_margin_usd"])
        if legacy_margin < Decimal("0.00"):
            legacy_negative_leakage_usd += abs(legacy_margin)
        codes = [c for c in row["applied_promo_codes"].split(",") if c]
        eval_res = evaluate_order_line_pricing(
            sku=row["sku"],
            qty=int(row["qty"]),
            promo_codes=codes,
            db_path=db_path,
        )
        recalculated_margin_usd += eval_res.gross_margin_usd
        if eval_res.gross_margin_pct >= eval_res.contract_min_margin_floor_pct:
            protected_orders_count += 1

    return {
        "margin_hold_orders_count": len(orders),
        "legacy_negative_margin_leakage_usd": float(legacy_negative_leakage_usd),
        "recalculated_total_margin_usd": float(recalculated_margin_usd),
        "protected_orders_count": protected_orders_count,
        "all_orders_margin_compliant": protected_orders_count == len(orders),
    }
