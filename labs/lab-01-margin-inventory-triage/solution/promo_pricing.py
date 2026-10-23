"""
Promotional Pricing & Commercial Margin Floor Engine (Lab 1 Reference Solution).

Fixes Bug #1A:
1. Uses exact Decimal arithmetic with ROUND_HALF_UP (2 decimal places).
2. Validates GS1 GTIN-14 check digit via validate_gs1_gtin14.
3. Filters out inactive (`active == 0`) or unknown promotional codes.
4. Enforces promo stacking rules:
   - Non-stackable promos (`is_stackable == 0`) cannot be combined with any other promo.
   - Stackable promos (`is_stackable == 1`) compound multiplicatively in descending order of discount_pct.
   - If both non-stackable and stackable promos are requested, selects whichever option yields the higher customer discount before floor clamping.
5. Enforces the effective minimum margin floor (`max(contract_min_margin_floor_pct, applied promo floors)`):
   - Clamps `net_revenue_usd` so `gross_margin_pct >= effective_min_margin_floor_pct` is strictly preserved.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from src.database import fetch_all, fetch_one
from src.models import PromoEvaluationResult, validate_gs1_gtin14

TWO_PLACES = Decimal("0.01")
HUNDRED = Decimal("100.00")


def _q2(val: Decimal | float | int | str) -> Decimal:
    return Decimal(str(val)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def evaluate_order_line_pricing(
    sku: str,
    qty: int = 1,
    promo_codes: list[str] | None = None,
    db_path: Path | None = None,
) -> PromoEvaluationResult:
    """
    Evaluate promotional discounts and enforce commercial margin floor for a SKU order line.
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

    gtin_14 = str(sku_row["gtin_14"])
    if not validate_gs1_gtin14(gtin_14):
        raise ValueError(f"Invalid GS1 GTIN-14 on SKU {sku}: {gtin_14}")

    # Deduplicate while preserving request order
    requested_codes: list[str] = []
    for raw in promo_codes or []:
        cleaned = raw.strip().upper()
        if cleaned and cleaned not in requested_codes:
            requested_codes.append(cleaned)

    unit_price = _q2(sku_row["unit_price_usd"])
    unit_cost = _q2(sku_row["unit_wholesale_cost_usd"])
    contract_floor_pct = _q2(sku_row["contract_min_margin_floor_pct"])

    gross_revenue = _q2(unit_price * Decimal(qty))
    total_wholesale_cost = _q2(unit_cost * Decimal(qty))

    valid_non_stackable: list[dict[str, Any]] = []
    valid_stackable: list[dict[str, Any]] = []
    rejected_codes: list[str] = []

    for code in requested_codes:
        promo_row = fetch_one(
            "SELECT * FROM promo_campaigns WHERE promo_code = ?",
            (code,),
            db_path=db_path,
        )
        if not promo_row or int(promo_row["active"]) != 1:
            rejected_codes.append(code)
            continue
        if int(promo_row["is_stackable"]) == 1:
            valid_stackable.append(promo_row)
        else:
            valid_non_stackable.append(promo_row)

    # Candidate A: Best single non-stackable promo
    best_non_stackable_net = gross_revenue
    best_non_stackable_row: dict[str, Any] | None = None
    if valid_non_stackable:
        valid_non_stackable.sort(key=lambda r: Decimal(str(r["discount_pct"])), reverse=True)
        best_non_stackable_row = valid_non_stackable[0]
        disc_rate = Decimal(str(best_non_stackable_row["discount_pct"])) / HUNDRED
        best_non_stackable_net = _q2(gross_revenue * (Decimal("1.00") - disc_rate))

    # Candidate B: Compounded stackable promos
    compounded_stackable_net = gross_revenue
    if valid_stackable:
        valid_stackable.sort(key=lambda r: Decimal(str(r["discount_pct"])), reverse=True)
        running = gross_revenue
        for st_row in valid_stackable:
            disc_rate = Decimal(str(st_row["discount_pct"])) / HUNDRED
            running = _q2(running * (Decimal("1.00") - disc_rate))
        compounded_stackable_net = running

    chosen_rows: list[dict[str, Any]] = []
    if valid_non_stackable and valid_stackable:
        # Compare customer benefit (lower net revenue before floor clamp wins)
        if best_non_stackable_net <= compounded_stackable_net and best_non_stackable_row is not None:
            chosen_rows = [best_non_stackable_row]
            candidate_net = best_non_stackable_net
        else:
            chosen_rows = list(valid_stackable)
            candidate_net = compounded_stackable_net
    elif valid_non_stackable and best_non_stackable_row is not None:
        chosen_rows = [best_non_stackable_row]
        candidate_net = best_non_stackable_net
    elif valid_stackable:
        chosen_rows = list(valid_stackable)
        candidate_net = compounded_stackable_net
    else:
        candidate_net = gross_revenue

    applied_codes = [str(r["promo_code"]) for r in chosen_rows]
    for code in requested_codes:
        if code not in applied_codes and code not in rejected_codes:
            rejected_codes.append(code)

    # Determine effective minimum margin floor %
    effective_floor_pct = contract_floor_pct
    for r in chosen_rows:
        promo_floor = _q2(r["min_margin_floor_pct"])
        if promo_floor > effective_floor_pct:
            effective_floor_pct = promo_floor

    # Minimum net revenue required so that (net_rev - cost) / net_rev >= effective_floor_pct / 100
    margin_ratio = effective_floor_pct / HUNDRED
    min_net_revenue = _q2(total_wholesale_cost / (Decimal("1.00") - margin_ratio))
    # Guard against 1-cent downward rounding dropping margin_pct by 0.01% below floor
    while _q2(((min_net_revenue - total_wholesale_cost) / min_net_revenue) * HUNDRED) < effective_floor_pct:
        min_net_revenue = _q2(min_net_revenue + TWO_PLACES)

    margin_floor_clamped = False
    if candidate_net < min_net_revenue:
        net_revenue = min_net_revenue
        margin_floor_clamped = True
    else:
        net_revenue = candidate_net

    if net_revenue > gross_revenue:
        net_revenue = gross_revenue

    discount_amount = _q2(gross_revenue - net_revenue)
    gross_margin_usd = _q2(net_revenue - total_wholesale_cost)
    gross_margin_pct = _q2((gross_margin_usd / net_revenue) * HUNDRED) if net_revenue > Decimal("0.00") else Decimal("-100.00")
    margin_compliant = gross_margin_pct >= contract_floor_pct and gross_margin_usd >= Decimal("0.00")

    return PromoEvaluationResult(
        sku=sku_row["sku"],
        gtin_14=gtin_14,
        qty=qty,
        unit_price_usd=unit_price,
        unit_wholesale_cost_usd=unit_cost,
        contract_min_margin_floor_pct=contract_floor_pct,
        requested_promo_codes=requested_codes,
        applied_promo_codes=applied_codes,
        rejected_promo_codes=rejected_codes,
        gross_revenue_usd=gross_revenue,
        discount_amount_usd=discount_amount,
        net_revenue_usd=net_revenue,
        total_wholesale_cost_usd=total_wholesale_cost,
        gross_margin_usd=gross_margin_usd,
        gross_margin_pct=gross_margin_pct,
        margin_floor_clamped=margin_floor_clamped,
        margin_compliant=margin_compliant,
    )


def audit_margin_hold_orders(db_path: Path | None = None) -> dict[str, Any]:
    """
    Scan all MARGIN_HOLD orders in omnichannel_orders and compare legacy recorded
    margins against the guarded promo pricing engine.
    """
    orders = fetch_all(
        "SELECT * FROM omnichannel_orders WHERE order_status = 'MARGIN_HOLD' ORDER BY order_id",
        db_path=db_path,
    )
    legacy_negative_leakage_usd = Decimal("0.00")
    recalculated_margin_usd = Decimal("0.00")
    protected_orders_count = 0

    for row in orders:
        legacy_margin = _q2(row["gross_margin_usd"])
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
