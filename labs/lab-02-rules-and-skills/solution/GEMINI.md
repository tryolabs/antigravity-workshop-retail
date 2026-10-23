<p align="center">
  <img src="../../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Retail Pulse — Omnichannel & Commercial Intelligence Workspace Rules

You are working inside **Retail Pulse**, an enterprise omnichannel commerce, WMS/POS inventory synchronization, and supplier commercial intelligence platform.

## 1. Domain Architecture & Data Sources
- **SQLite Database**: `data/retail_pulse.db` accessed via `src/database.py`.
  - `sku_catalog`: 25 SKUs with 14-digit GS1 `gtin_14`, `rfid_epc_prefix`, `unit_wholesale_cost_usd`, `unit_price_usd`, and `contract_min_margin_floor_pct`.
  - `wms_inventory`: 150 location-SKU records across 6 fulfillment centers (`WH-EAST-NJ01`, `WH-WEST-CA02`, `WH-CENTRAL-TX03`, `STORE-NYC-5TH`, `STORE-CHI-MAG`, `STORE-MIA-BRICKELL`) tracking `on_hand_qty`, `reserved_qty`, `safety_stock_qty`, and `unprocessed_webhook_delta_qty`.
  - `vendor_contracts`: 10 supplier commercial agreements tracking `annual_spend_commitment_usd`, `contract_min_margin_floor_pct`, `otif_target_pct`, `actual_otif_pct`, `delayed_po_value_usd`, and `chargeback_penalty_pct`.
  - `promo_campaigns`: Promotional campaigns with `discount_pct`, `is_stackable`, `min_margin_floor_pct`, and `active`.
  - `omnichannel_orders`: 200 sales orders across `WEB_ECOMM`, `MOBILE_APP`, `POS_INSTORE`, and `BOPIS` with `loyalty_tier` (`DIAMOND`, `GOLD`, `SILVER`, `STANDARD`) and `customer_ltv_usd`.
- **Telemetry & EDI Logs**: `data/logs/pos_wms_webhooks.jsonl` containing `POS_CHECKOUT_WEBHOOK_LAG` and `EDI_856_ASN_AUDIT` events.

## 2. Non-Negotiable Engineering & Commercial Guardrails
1. **Exact Currency & Margin Arithmetic (`Decimal` + `ROUND_HALF_UP`)**:
   - Never use IEEE-754 `float` for pricing, promotional discounts, gross margin percentages, or vendor OTIF chargebacks.
   - Always use `decimal.Decimal` quantized to `Decimal("0.01")` with `ROUND_HALF_UP`.
2. **GS1 GTIN-14 Check-Digit Validation**:
   - Every SKU `gtin_14` must be a valid 14-digit GS1 identifier verified via `validate_gs1_gtin14()` in `src/models.py` (Modulo-10 weighting 3,1,3,1...).
3. **Contract Minimum Margin Floor Protection**:
   - No promotional code or split-fulfillment shipping allocation may reduce net order margin below `contract_min_margin_floor_pct`.
   - Non-stackable promotional codes (`is_stackable == 0`) must never stack together; stackable promos (`is_stackable == 1`) compound multiplicatively.
4. **True Available-to-Promise (ATP) Inventory Formula**:
   - Always calculate True ATP as:
     `true_atp_qty = max(0, on_hand_qty - reserved_qty - safety_stock_qty - unprocessed_webhook_delta_qty)`
5. **VIP Customer LTV Prioritization**:
   - When resolving `AT_RISK_STOCKOUT` orders, always prioritize `DIAMOND` and `GOLD` loyalty tiers ordered by `customer_ltv_usd DESC`.
