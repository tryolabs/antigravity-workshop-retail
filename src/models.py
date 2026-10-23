"""Pydantic domain models and GS1 GTIN-14 validators for Retail Pulse."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator


def validate_gs1_gtin14(gtin_14: str) -> bool:
    """Validate a 14-digit GS1 GTIN-14 string using the standard Modulo-10 check digit."""
    if not isinstance(gtin_14, str) or len(gtin_14) != 14 or not gtin_14.isdigit():
        return False
    total = 0
    for idx, ch in enumerate(gtin_14[:13]):
        multiplier = 3 if idx % 2 == 0 else 1
        total += int(ch) * multiplier
    check_digit = (10 - (total % 10)) % 10
    return check_digit == int(gtin_14[13])


class PromoEvaluationRequest(BaseModel):
    sku: str = Field(..., description="SKU identifier from sku_catalog")
    qty: int = Field(default=1, ge=1, description="Order line quantity")
    promo_codes: list[str] = Field(default_factory=list, description="Requested promotional codes")


class PromoEvaluationResult(BaseModel):
    sku: str
    gtin_14: str
    qty: int
    unit_price_usd: Decimal
    unit_wholesale_cost_usd: Decimal
    contract_min_margin_floor_pct: Decimal
    requested_promo_codes: list[str]
    applied_promo_codes: list[str]
    rejected_promo_codes: list[str]
    gross_revenue_usd: Decimal
    discount_amount_usd: Decimal
    net_revenue_usd: Decimal
    total_wholesale_cost_usd: Decimal
    gross_margin_usd: Decimal
    gross_margin_pct: Decimal
    margin_floor_clamped: bool
    margin_compliant: bool

    @field_validator("gtin_14")
    @classmethod
    def check_valid_gtin14(cls, value: str) -> str:
        if not validate_gs1_gtin14(value):
            raise ValueError(f"Invalid GS1 GTIN-14 check digit: {value}")
        return value


class ATPCalculationResult(BaseModel):
    inventory_id: str
    location_id: str
    location_type: str
    sku: str
    gtin_14: str
    product_name: str
    category: str
    on_hand_qty: int
    reserved_qty: int
    safety_stock_qty: int
    unprocessed_webhook_delta_qty: int
    raw_atp_qty: int
    true_atp_qty: int
    oversell_risk: bool
    shipping_cost_usd: Decimal


class VendorOTIFAuditRecord(BaseModel):
    contract_id: str
    vendor_name: str
    category: str
    buyer_id: str
    annual_spend_commitment_usd: Decimal
    contract_min_margin_floor_pct: Decimal
    otif_target_pct: Decimal
    actual_otif_pct: Decimal
    otif_gap_pct: Decimal
    late_shipments_count: int
    short_shipments_count: int
    delayed_po_value_usd: Decimal
    chargeback_penalty_pct: Decimal
    recoverable_chargeback_usd: Decimal
    edi_856_asn_alerts_count: int
    status: str
    recommended_action: str


class OrderRoutingDecision(BaseModel):
    order_id: str
    customer_id: str
    loyalty_tier: str
    customer_ltv_usd: Decimal
    sku: str
    qty: int
    original_location_id: str
    original_location_true_atp: int
    assigned_location_id: str
    assigned_location_true_atp: int
    shipping_cost_usd: Decimal
    post_shipping_margin_usd: Decimal
    post_shipping_margin_pct: Decimal
    contract_min_margin_floor_pct: Decimal
    margin_floor_preserved: bool
    routing_status: str


class ChargebackClaimDecision(BaseModel):
    claim_id: str
    contract_id: str
    vendor_name: str
    category: str
    otif_target_pct: Decimal
    actual_otif_pct: Decimal
    otif_shortfall_pct: Decimal
    delayed_po_value_usd: Decimal
    chargeback_penalty_pct: Decimal
    claim_amount_usd: Decimal
    edi_asn_evidence_count: int
    claim_status: str
