"""
Lab 1 Verification Suite: Promotional Margin Floor Guard & True ATP Inventory Triage.
"""

from __future__ import annotations

from decimal import Decimal

from src.models import validate_gs1_gtin14
from src.services.inventory_atp import (
    audit_vip_oversell_exposure,
    calculate_location_atp,
)
from src.services.promo_pricing import (
    audit_margin_hold_orders,
    evaluate_order_line_pricing,
)


def test_gs1_gtin14_check_digit_validator() -> None:
    assert validate_gs1_gtin14("00012345678905") is True
    assert validate_gs1_gtin14("00012345678900") is False
    assert validate_gs1_gtin14("12345") is False


def test_non_stackable_promos_and_margin_floor_clamping() -> None:
    """
    Bug 1A Check:
    Passing 'VIP25,FLASH20,EMP30' on SKU-SONY-OLED65 ($1,799 retail, $1,120 wholesale,
    22% contract min margin floor) must:
    1. Reject combining multiple non-stackable promo codes (only 1 non-stackable code may apply).
    2. Clamp net_revenue_usd so gross_margin_pct >= 22.00% (never selling below wholesale cost!).
    """
    res = evaluate_order_line_pricing(
        sku="SKU-SONY-OLED65",
        qty=2,
        promo_codes=["VIP25", "FLASH20", "EMP30"],
    )
    assert len(res.applied_promo_codes) == 1
    assert "EMP30" in res.applied_promo_codes
    assert "VIP25" in res.rejected_promo_codes
    assert "FLASH20" in res.rejected_promo_codes
    assert res.margin_floor_clamped is True
    assert res.margin_compliant is True
    assert res.gross_margin_usd > Decimal("0.00")
    assert res.gross_margin_pct >= res.contract_min_margin_floor_pct


def test_stackable_promos_compound_and_reject_expired() -> None:
    """
    Stackable promos (HOLIDAY15, BUNDLE10, LOYALTY5) should compound multiplicatively,
    while inactive promos (EXPIRED50) must be rejected.
    """
    res = evaluate_order_line_pricing(
        sku="SKU-LEVI-501SEL",
        qty=1,
        promo_codes=["HOLIDAY15", "BUNDLE10", "EXPIRED50"],
    )
    assert "EXPIRED50" in res.rejected_promo_codes
    assert set(res.applied_promo_codes) == {"HOLIDAY15", "BUNDLE10"}
    assert res.gross_margin_pct >= res.contract_min_margin_floor_pct
    assert res.margin_compliant is True


def test_audit_margin_hold_orders_eliminates_negative_leakage() -> None:
    summary = audit_margin_hold_orders()
    assert summary["margin_hold_orders_count"] == 30
    assert summary["legacy_negative_margin_leakage_usd"] >= 34000.0
    assert summary["all_orders_margin_compliant"] is True
    assert summary["recalculated_total_margin_usd"] > 0.0


def test_true_atp_deducts_reserved_safety_and_webhook_lag() -> None:
    """
    Bug 1B Check:
    At STORE-NYC-5TH, SKU-SONY-OLED65 has on_hand=14, reserved=6, safety_stock=4,
    unprocessed_webhook_delta_qty=5 -> raw_atp = -1 -> true_atp_qty = 0, oversell_risk = True.
    """
    nyc_atp = calculate_location_atp(sku="SKU-SONY-OLED65", location_id="STORE-NYC-5TH", required_qty=1)
    assert nyc_atp.on_hand_qty == 14
    assert nyc_atp.reserved_qty == 6
    assert nyc_atp.safety_stock_qty == 4
    assert nyc_atp.unprocessed_webhook_delta_qty == 5
    assert nyc_atp.raw_atp_qty == -1
    assert nyc_atp.true_atp_qty == 0
    assert nyc_atp.oversell_risk is True

    tx_atp = calculate_location_atp(sku="SKU-SONY-OLED65", location_id="WH-CENTRAL-TX03", required_qty=2)
    assert tx_atp.true_atp_qty >= 60
    assert tx_atp.oversell_risk is False


def test_vip_oversell_exposure_detects_all_at_risk_orders() -> None:
    exposure = audit_vip_oversell_exposure()
    assert exposure["at_risk_orders_total"] == 35
    assert exposure["detected_oversell_orders_count"] == 35
    assert exposure["exposed_customer_ltv_usd"] >= 250000.0
