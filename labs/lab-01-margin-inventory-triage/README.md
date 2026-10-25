<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Lab 01: Promotional Margin Floor & True ATP Inventory Triage

**Delivered by Tryolabs • Powered by Google Antigravity & Gemini Enterprise**

> **Language / Idioma:** [English](./README.md) | [Español](./README.es.md) • **Prompt Playbook:** [PROMPTS.md](./PROMPTS.md) | [PROMPTS.es.md](./PROMPTS.es.md) • **PDF:** [EN](./LAB_01_INSTRUCTIONS_EN.pdf) | [ES](./LAB_01_INSTRUCTIONS_ES.pdf)

---

## 1. Scenario & Business Impact

During our weekend omnichannel flash event, **Retail Pulse** experienced two severe production incidents across `WEB_ECOMM`, `MOBILE_APP`, `POS_INSTORE`, and `BOPIS`:

1. **Incident #1A — Promotional Margin Bleed (`src/services/promo_pricing.py`)**:
   - Customers stacked three non-stackable promotional codes (`VIP25`, `FLASH20`, `EMP30`) simultaneously.
   - The pricing engine added their percentages linearly (`25% + 20% + 30% = 75%` off!) using binary `float` math and completely ignored the supplier `contract_min_margin_floor_pct`.
   - Result: **30 `MARGIN_HOLD` orders are bleeding `-$35,113.25` below wholesale cost!**
2. **Incident #1B — Phantom-Stock VIP Overselling (`src/services/inventory_atp.py`)**:
   - Flagship stores (`STORE-NYC-5TH`, `STORE-MIA-BRICKELL`) and `WH-EAST-NJ01` experienced POS terminal webhook lag (`unprocessed_webhook_delta_qty` logged in `data/logs/pos_wms_webhooks.jsonl`).
   - The Available-to-Promise (ATP) calculator naively returned `on_hand_qty` without subtracting `reserved_qty`, `safety_stock_qty`, and `unprocessed_webhook_delta_qty`.
   - Result: **35 `DIAMOND` and `GOLD` loyalty orders (`>$250,000` in Customer LTV) were promised stock at locations where True ATP is `0` (`raw_atp = -1`)!**

---

## 2. Lab Setup

Run the Lab 01 installer from the repository root to initialize the starter bugs and SQLite database:

```bash
./labs/lab-01-margin-inventory-triage/install.sh
```

Verify that the starter test suite currently fails on both bugs:

```bash
./.venv/bin/pytest tests/test_lab01_triage.py
```

Optional — launch the Live Omnichannel Command Center Dashboard in a second terminal:

```bash
./.venv/bin/uvicorn src.main:app --reload --port 8002
```
Open `http://localhost:8002` to observe the red `BUG #1A ACTIVE` and `BUG #1B ACTIVE` KPI banners.

---

## 3. Step-by-Step Resolution Using Google Antigravity

Open [PROMPTS.md](./PROMPTS.md) and paste the prompts into **Google Antigravity** (Sidebar Chat, `/plan`, or Inline `Cmd+I`):

### Step 3.1: Root-Cause Discovery with `@` Context Mentions
Paste the **Discovery Prompt** from `PROMPTS.md` referencing `@src/services/promo_pricing.py`, `@src/services/inventory_atp.py`, `@data/logs/pos_wms_webhooks.jsonl`, and `@tests/test_lab01_triage.py`.

### Step 3.2: Structured Remediation Plan with `/plan`
Run the **`/plan` Prompt** in Antigravity to verify the exact mathematical and commercial requirements before editing code:
- **Fix #1A (`src/services/promo_pricing.py`)**:
  - Use `Decimal` with `ROUND_HALF_UP` (`Decimal("0.01")`) and validate SKU `gtin_14` via `validate_gs1_gtin14`.
  - Reject inactive (`active == 0`) or unknown promo codes into `rejected_promo_codes`.
  - Never combine non-stackable promos (`is_stackable == 0`). Compare the single highest non-stackable promo against multiplicatively compounded stackable promos (`is_stackable == 1`), selecting whichever gives the customer the best pre-clamped discount.
  - Enforce the effective margin floor (`max(contract_min_margin_floor_pct, applied promo floors)`): clamp `net_revenue_usd` so `gross_margin_pct >= effective_floor_pct` and set `margin_floor_clamped = True`.
- **Fix #1B (`src/services/inventory_atp.py`)**:
  - Compute `raw_atp_qty = on_hand_qty - reserved_qty - safety_stock_qty - unprocessed_webhook_delta_qty`.
  - Compute `true_atp_qty = max(0, raw_atp_qty)`.
  - Flag `oversell_risk = (true_atp_qty < required_qty) or (raw_atp_qty <= 0)`.

### Step 3.3: Apply Fixes & Verify
Let Antigravity implement the fixes (or use `Cmd+I` inline edit inside `src/services/promo_pricing.py` and `src/services/inventory_atp.py`), then run:

```bash
./labs/lab-01-margin-inventory-triage/verify.sh
```

> **Need to check the reference solution?** Run `./labs/lab-01-margin-inventory-triage/apply_solution.sh` at any time.
