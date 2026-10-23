<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Lab 01 — Optimized Antigravity Prompts Playbook (English)

Use these copy-pasteable prompts inside **Google Antigravity** (Sidebar Chat, `/plan`, Inline `Cmd+I`, or CLI `agy`) to complete Lab 01.

---

## 1. Discovery Prompt (Root-Cause Triage with `@` Mentions)

```text
Inspect @src/services/promo_pricing.py, @src/services/inventory_atp.py, @data/logs/pos_wms_webhooks.jsonl, and @tests/test_lab01_triage.py.
Run pytest on tests/test_lab01_triage.py and explain:
1. Why 30 MARGIN_HOLD orders in omnichannel_orders are losing -$35,113.25 below wholesale cost when promo codes like VIP25, FLASH20, and EMP30 are passed together.
2. Why 35 DIAMOND and GOLD VIP orders at STORE-NYC-5TH and WH-EAST-NJ01 are suffering phantom-stock overselling due to POS webhook sync lag.
```

---

## 2. `/plan` Prompt (Structured Remediation Plan)

```text
/plan Create a step-by-step plan to fix both Bug #1A in @src/services/promo_pricing.py and Bug #1B in @src/services/inventory_atp.py so all tests in @tests/test_lab01_triage.py pass:
1. In promo_pricing.py:
   - Use Decimal quantized to Decimal("0.01") with ROUND_HALF_UP and validate GS1 GTIN-14 check digits via validate_gs1_gtin14().
   - Reject inactive (active != 1) or unknown promo codes in rejected_promo_codes.
   - Enforce promo stacking rules: non-stackable promos (is_stackable == 0) cannot stack with any other code; stackable promos (is_stackable == 1) compound multiplicatively. Pick whichever valid option gives the customer the best pre-clamped discount.
   - Clamp net_revenue_usd so gross_margin_pct never drops below max(contract_min_margin_floor_pct, applied promo floors), setting margin_floor_clamped = True when clamped.
2. In inventory_atp.py:
   - Compute raw_atp_qty = on_hand_qty - reserved_qty - safety_stock_qty - unprocessed_webhook_delta_qty.
   - Set true_atp_qty = max(0, raw_atp_qty) and oversell_risk = (true_atp_qty < required_qty) or (raw_atp_qty <= 0).
```

---

## 3. Inline `Cmd+I` Prompt (Targeted In-Editor Fix for `inventory_atp.py`)

Highlight `calculate_location_atp` in `src/services/inventory_atp.py`, press `Cmd+I` (macOS) / `Ctrl+I` (Windows/Linux), and enter:

```text
Validate gtin_14 using validate_gs1_gtin14(), compute raw_atp = on_hand - reserved - safety_stock - webhook_delta, clamp true_atp = max(0, raw_atp), and set oversell_risk = (true_atp < required_qty) or (raw_atp <= 0).
```

---

## 4. Implementation & Verification Prompt

```text
Implement the full fixes in @src/services/promo_pricing.py and @src/services/inventory_atp.py according to the plan, then run ./labs/lab-01-margin-inventory-triage/verify.sh to confirm all 6 tests in test_lab01_triage.py pass 100%.
```

---

## 5. Power-User & Stretch Prompts (`/grill-me`, `/browser`, `/learn`)

### 5A. Interactive Edge-Case Stress Test (`/grill-me`)
```text
/grill-me Interview me on promotional stacking edge cases for omnichannel retail (e.g., BOGO bundles, employee discounts combined with clearance items, and rounding edge cases when clamping net revenue to the exact penny on multi-unit orders).
```

### 5B. Live Dashboard Visual Verification (`/browser`)
```text
/browser Open http://localhost:8002, verify that the "1. Promo Margin Floor Guard" and "2. True ATP & VIP Oversell Radar" KPI cards now show PROTECTED and TRUE ATP ACTIVE, and test SKU-SONY-OLED65 with promo codes VIP25,FLASH20,EMP30 in the Interactive Promo Simulator.
```

### 5C. Persist Fix Learnings (`/learn`)
```text
/learn Persist the rule that all Retail Pulse pricing calculations must use Decimal(ROUND_HALF_UP) and enforce contract_min_margin_floor_pct clamping, and that ATP calculations must always subtract reserved_qty, safety_stock_qty, and unprocessed_webhook_delta_qty.
```
