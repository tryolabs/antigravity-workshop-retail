<p align="center">
  <img src="../../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Retail Pulse Coding & Commercial Governance Standards

## 1. Financial & Margin Precision (`Decimal`)
- All monetary values (`unit_price_usd`, `unit_wholesale_cost_usd`, `discount_amount_usd`, `net_revenue_usd`, `gross_margin_usd`, `shipping_cost_usd`, `recoverable_chargeback_usd`) MUST use `decimal.Decimal` with `ROUND_HALF_UP`.
- Never allow a promotional discount to violate `contract_min_margin_floor_pct`. If a discount would breach the floor, clamp `net_revenue_usd` to the minimum compliant revenue and set `margin_floor_clamped = True`.

## 2. GS1 GTIN-14 & RFID Standards
- All SKUs must carry a 14-digit `gtin_14` string passing the GS1 Modulo-10 check digit algorithm (`validate_gs1_gtin14`).
- Preserve `rfid_epc_prefix` (`urn:epc:id:sgtin:...`) when querying or exporting WMS inventory snapshots.

## 3. True Available-to-Promise (ATP) & POS Webhook Drift
- Never expose raw `on_hand_qty` as Available-to-Promise.
- Always deduct `reserved_qty`, `safety_stock_qty`, and `unprocessed_webhook_delta_qty` (caused by lagging in-store POS checkout webhooks) before promising stock to omnichannel orders.

## 4. Supplier OTIF & EDI 856 ASN Auditing
- When a vendor's `actual_otif_pct < otif_target_pct`, flag the contract as `BREACH_HOLD` and compute recoverable chargebacks as:
  `recoverable_chargeback_usd = delayed_po_value_usd * (chargeback_penalty_pct / 100)`
- Cross-reference every OTIF chargeback claim with `EDI_856_ASN_AUDIT` events in `data/logs/pos_wms_webhooks.jsonl`.
