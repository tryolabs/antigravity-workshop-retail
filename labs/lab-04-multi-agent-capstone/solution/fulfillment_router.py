"""
Intelligent Omnichannel Split-Fulfillment & Vendor Chargeback Engine (Lab 4 Reference Solution).

Implements:
1. `optimize_at_risk_order_routing()`:
   - Prioritizes AT_RISK_STOCKOUT orders by loyalty tier (DIAMOND > GOLD > SILVER > STANDARD)
     and descending customer_ltv_usd.
   - Evaluates True ATP (`on_hand - reserved - safety_stock - webhook_delta`) across all
     fulfillment locations, tracking real-time allocations during the batch run.
   - Selects the lowest-shipping-cost alternate warehouse/store with `true_atp_qty >= qty`
     that preserves `post_shipping_margin_pct >= contract_min_margin_floor_pct`.
2. `claim_vendor_otif_chargebacks()`:
   - Cross-references breaching vendor OTIF contracts with EDI 856 ASN evidence logs
     and computes exact Decimal chargeback penalty claims.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from src.database import execute_write, fetch_all, fetch_one
from src.models import ChargebackClaimDecision, OrderRoutingDecision
from src.services.inventory_atp import calculate_location_atp, get_sku_network_atp
from src.services.promo_pricing import evaluate_order_line_pricing
from src.services.vendor_otif_auditor import audit_vendor_contracts

TWO_PLACES = Decimal("0.01")
HUNDRED = Decimal("100.00")

TIER_PRIORITY = {
    "DIAMOND": 1,
    "GOLD": 2,
    "SILVER": 3,
    "STANDARD": 4,
}


def _q2(val: Decimal | float | int | str) -> Decimal:
    return Decimal(str(val)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def optimize_at_risk_order_routing(
    loyalty_tiers: list[str] | None = None,
    persist_changes: bool = False,
    db_path: Path | None = None,
) -> dict[str, Any]:
    """
    Evaluate and reroute AT_RISK_STOCKOUT orders by prioritizing high-LTV VIP customers,
    selecting alternate fulfillment nodes with sufficient True ATP, and verifying that
    shipping costs do not breach the SKU's contract minimum margin floor.
    """
    orders = fetch_all(
        "SELECT * FROM omnichannel_orders WHERE order_status = 'AT_RISK_STOCKOUT'",
        db_path=db_path,
    )
    if loyalty_tiers:
        allowed = {t.strip().upper() for t in loyalty_tiers if t.strip()}
        orders = [o for o in orders if str(o["loyalty_tier"]).upper() in allowed]

    # Sort by loyalty tier priority (DIAMOND -> GOLD -> SILVER -> STANDARD) then customer_ltv_usd DESC
    orders.sort(
        key=lambda r: (
            TIER_PRIORITY.get(str(r["loyalty_tier"]).upper(), 99),
            -float(r["customer_ltv_usd"]),
            str(r["order_id"]),
        )
    )

    # Track in-memory inventory allocations across the optimization batch
    allocated_tracker: dict[tuple[str, str], int] = {}

    decisions: list[OrderRoutingDecision] = []
    rerouted_count = 0
    protected_ltv_usd = Decimal("0.00")
    total_post_shipping_margin_usd = Decimal("0.00")

    for order in orders:
        order_id = str(order["order_id"])
        sku = str(order["sku"])
        qty = int(order["qty"])
        orig_loc = str(order["fulfillment_location_id"])
        tier = str(order["loyalty_tier"])
        ltv = _q2(order["customer_ltv_usd"])

        sku_row = fetch_one("SELECT * FROM sku_catalog WHERE sku = ?", (sku,), db_path=db_path)
        contract_floor_pct = _q2(sku_row["contract_min_margin_floor_pct"]) if sku_row else Decimal("20.00")

        # Evaluate guarded order pricing to ensure net revenue & wholesale cost are accurate
        promo_codes = [c for c in str(order["applied_promo_codes"]).split(",") if c]
        pricing = evaluate_order_line_pricing(sku=sku, qty=qty, promo_codes=promo_codes, db_path=db_path)

        orig_atp_obj = calculate_location_atp(sku=sku, location_id=orig_loc, required_qty=qty, db_path=db_path)
        already_taken_orig = allocated_tracker.get((sku, orig_loc), 0)
        orig_effective_atp = max(0, orig_atp_obj.true_atp_qty - already_taken_orig)

        # Find candidate locations across the network
        network_atp = get_sku_network_atp(sku=sku, required_qty=qty, db_path=db_path)
        valid_candidates = []
        for cand in network_atp:
            taken = allocated_tracker.get((sku, cand.location_id), 0)
            eff_atp = max(0, cand.true_atp_qty - taken)
            if eff_atp >= qty:
                post_ship_margin = _q2(pricing.gross_margin_usd - cand.shipping_cost_usd)
                post_ship_pct = (
                    _q2((post_ship_margin / pricing.net_revenue_usd) * HUNDRED)
                    if pricing.net_revenue_usd > Decimal("0.00")
                    else Decimal("-100.00")
                )
                margin_ok = post_ship_pct >= contract_floor_pct and post_ship_margin > Decimal("0.00")
                valid_candidates.append(
                    (
                        not margin_ok,  # Prefer margin-compliant candidates first (False < True)
                        cand.shipping_cost_usd,  # Lowest shipping cost
                        -eff_atp,  # Highest available True ATP tie-breaker
                        cand,
                        eff_atp,
                        post_ship_margin,
                        post_ship_pct,
                        margin_ok,
                    )
                )

        if valid_candidates:
            valid_candidates.sort(key=lambda item: (item[0], item[1], item[2]))
            _, ship_cost, _, chosen_cand, chosen_eff_atp, post_margin, post_pct, margin_ok = valid_candidates[0]
            assigned_loc = chosen_cand.location_id
            allocated_tracker[(sku, assigned_loc)] = allocated_tracker.get((sku, assigned_loc), 0) + qty
            status = "REROUTED_MARGIN_PROTECTED" if margin_ok else "REROUTED_MARGIN_EXCEPTION"
            rerouted_count += 1
            protected_ltv_usd = _q2(protected_ltv_usd + ltv)
            total_post_shipping_margin_usd = _q2(total_post_shipping_margin_usd + post_margin)

            if persist_changes:
                execute_write(
                    """
                    UPDATE omnichannel_orders
                    SET fulfillment_location_id = ?, order_status = 'FULFILLED'
                    WHERE order_id = ?
                    """,
                    (assigned_loc, order_id),
                    db_path=db_path,
                )
        else:
            assigned_loc = orig_loc
            chosen_eff_atp = orig_effective_atp
            ship_cost = orig_atp_obj.shipping_cost_usd
            post_margin = _q2(pricing.gross_margin_usd - ship_cost)
            post_pct = (
                _q2((post_margin / pricing.net_revenue_usd) * HUNDRED)
                if pricing.net_revenue_usd > Decimal("0.00")
                else Decimal("-100.00")
            )
            margin_ok = False
            status = "BACKORDER_UNROUTABLE"

        decisions.append(
            OrderRoutingDecision(
                order_id=order_id,
                customer_id=str(order["customer_id"]),
                loyalty_tier=tier,
                customer_ltv_usd=ltv,
                sku=sku,
                qty=qty,
                original_location_id=orig_loc,
                original_location_true_atp=orig_effective_atp,
                assigned_location_id=assigned_loc,
                assigned_location_true_atp=chosen_eff_atp,
                shipping_cost_usd=ship_cost,
                post_shipping_margin_usd=post_margin,
                post_shipping_margin_pct=post_pct,
                contract_min_margin_floor_pct=contract_floor_pct,
                margin_floor_preserved=margin_ok,
                routing_status=status,
            )
        )

    return {
        "status": "OPTIMIZED",
        "evaluated_orders_count": len(decisions),
        "rerouted_orders_count": rerouted_count,
        "protected_customer_ltv_usd": float(protected_ltv_usd),
        "total_post_shipping_margin_usd": float(total_post_shipping_margin_usd),
        "decisions": [d.model_dump(mode="json") for d in decisions],
    }


def claim_vendor_otif_chargebacks(
    min_shortfall_pct: float = 0.0,
    db_path: Path | None = None,
) -> dict[str, Any]:
    """
    Generate formal Vendor OTIF Chargeback Debit Memos for suppliers breaching their
    contractual OTIF target percentage, backed by EDI 856 ASN delay/shortage logs.
    """
    audit_res = audit_vendor_contracts(only_breaching=True, db_path=db_path)
    min_gap = _q2(min_shortfall_pct)

    claims: list[ChargebackClaimDecision] = []
    total_claim_usd = Decimal("0.00")

    seq = 1
    for rec in audit_res["contracts"]:
        gap_pct = _q2(rec["otif_gap_pct"])
        if gap_pct < min_gap:
            continue
        claim_amt = _q2(rec["recoverable_chargeback_usd"])
        total_claim_usd = _q2(total_claim_usd + claim_amt)
        claim_id = f"CLM-2026-{seq:03d}"
        seq += 1

        claims.append(
            ChargebackClaimDecision(
                claim_id=claim_id,
                contract_id=str(rec["contract_id"]),
                vendor_name=str(rec["vendor_name"]),
                category=str(rec["category"]),
                otif_target_pct=_q2(rec["otif_target_pct"]),
                actual_otif_pct=_q2(rec["actual_otif_pct"]),
                otif_shortfall_pct=gap_pct,
                delayed_po_value_usd=_q2(rec["delayed_po_value_usd"]),
                chargeback_penalty_pct=_q2(rec["chargeback_penalty_pct"]),
                claim_amount_usd=claim_amt,
                edi_asn_evidence_count=int(rec["edi_856_asn_alerts_count"]),
                claim_status="DEBIT_MEMO_READY",
            )
        )

    return {
        "status": "CLAIMS_GENERATED",
        "breaching_vendors_count": len(claims),
        "total_claim_amount_usd": float(total_claim_usd),
        "claims": [c.model_dump(mode="json") for c in claims],
    }
