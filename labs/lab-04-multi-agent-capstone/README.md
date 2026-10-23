# Lab 04: Multi-Agent Capstone — Smart Split-Shipment Routing & Executive Command Center

**Duration**: 45 Minutes | **Persona**: Technical & Commercial Track | **Prerequisites**: Labs 01, 02 & 03 Completed

---

## 1. Retail Scenario & Business Context

In Labs 01–03, your team stabilized promotional margin floors, repaired True ATP inventory calculations, encoded retail compliance standards (`GEMINI.md`, `.agents/rules/retail-standards.md`, `.agents/skills/retail-otif-margin-auditor/SKILL.md`), and connected Antigravity to `retail_pulse.db` via FastMCP and deterministic `PreToolUse` hooks.

However, **35 VIP orders (`DIAMOND` and `GOLD` loyalty tiers)** representing **over $250,000 in Customer Lifetime Value (LTV)** are still stuck in `AT_RISK_STOCKOUT` status because their original flagship store node lacked sufficient True ATP inventory!

Previously, the legacy OMS simply cancelled any order whose primary node could not fulfill it. Your capstone mission is to use **Antigravity's Multi-Agent Orchestration** (`/plan`, `/boost`, `/teamwork`, subagents, and `/browser`) to build the **Smart Omnichannel Split-Shipment & Rerouting Engine** (`src/services/fulfillment_router.py`), expose it via `/api/v1/fulfillment/optimize-routing`, and verify the live executive KPI recovery in the **Retail Pulse Command Center**.

---

## 2. Learning Objectives

In this capstone lab, you will:
1. Use `/plan` and `/boost` (or `/teamwork` parallel subagents) to design and implement `evaluate_candidates` and `optimize_at_risk_orders` in `src/services/fulfillment_router.py`.
2. Rank candidate fulfillment nodes (`DC` and `STORE`) where `true_atp >= order_qty` by highest **Post-Shipping Net Margin USD** (using node `shipping_zone_cost_usd` and breaking ties by lowest shipping cost / `DC` priority).
3. Automatically reroute all 35 `AT_RISK_STOCKOUT` VIP orders to `REROUTED_OPTIMAL` while decrementing `on_hand_qty` at the winning fulfillment node and generating `$14,774.00` in preserved post-shipping net margin.
4. Verify the end-to-end recovery via `pytest` (`./labs/lab-04-multi-agent-capstone/verify.sh`) and visually inspect the live **Retail Pulse Command Center** (`http://127.0.0.1:8000`) using `/browser`.

---

## 3. Step-by-Step Instructions

### Step 1: Initialize the Lab 04 Starter State

Run the Lab 04 installer to ensure Labs 01, 02, and 03 solutions are applied and load the Lab 04 starter stub for `src/services/fulfillment_router.py`:

```bash
./labs/lab-04-multi-agent-capstone/install.sh
```

Run the verification script to observe the failing capstone tests (`NotImplementedError` in `evaluate_candidates` and `optimize_at_risk_orders`):

```bash
./labs/lab-04-multi-agent-capstone/verify.sh
```

---

### Step 2: Inspect the Capstone Requirements

Open `src/services/fulfillment_router.py` and `tests/test_lab04_capstone.py`.
Review the business logic required for the two functions in `src/services/fulfillment_router.py`:

1. **`evaluate_candidates(conn, sku, qty, effective_unit_price_usd)`**:
   - Query `wms_inventory` for all nodes holding `sku`.
   - Compute `true_atp` using `calculate_node_atp(dict(row))` from `src.services.inventory_atp`.
   - Filter to eligible nodes where `true_atp >= qty`.
   - For each eligible node, compute:
     - `shipping_cost_usd = round(float(row["shipping_zone_cost_usd"]), 2)`
     - `gross_margin_usd = (effective_unit_price_usd - unit_cost_usd) * qty`
     - `post_shipping_net_margin_usd = round(gross_margin_usd - shipping_cost_usd, 2)`
   - Sort eligible candidates by:
     1. Highest `post_shipping_net_margin_usd` (`-c["post_shipping_net_margin_usd"]`)
     2. Lowest `shipping_cost_usd` (`c["shipping_cost_usd"]`)
     3. Warehouse DC preference (`0 if c["location_type"] == "DC" else 1`)

2. **`optimize_at_risk_orders(conn, dry_run=False)`**:
   - Query `omnichannel_orders` where `status = 'AT_RISK_STOCKOUT'` ordered by `customer_ltv_usd DESC, order_id ASC`.
   - For each order, call `evaluate_candidates(conn, sku, qty, effective_unit_price_usd)`:
     - Select the top candidate (`best = candidates[0]`).
     - If `not dry_run`:
       - Update `omnichannel_orders` setting `assigned_node_id = best["location_id"]`, `status = 'REROUTED_OPTIMAL'`, and `fulfillment_notes` with a clear audit note including `best["location_id"]` and `best["post_shipping_net_margin_usd"]`.
       - Decrement `on_hand_qty = on_hand_qty - qty` in `wms_inventory` for `(sku, best["location_id"])`.
   - Commit if `not dry_run` and return the summary dictionary (`total_at_risk_evaluated`, `rerouted_count`, `unfulfillable_count`, `vip_ltv_saved_usd`, `total_post_shipping_net_margin_usd`, `decisions`).

---

### Step 3: Orchestrate Multi-Agent Implementation (`/plan`, `/boost`, `/teamwork`)

Open `labs/lab-04-multi-agent-capstone/PROMPTS.md` and run the **Multi-Agent Capstone Prompts**:
- Start with `/plan` or `/boost` to design the candidate evaluation and inventory reservation transaction.
- Or use `/teamwork` to coordinate parallel subagents:
  - **Subagent 1 (Fulfillment Routing Engineer)**: Implements `evaluate_candidates` and `optimize_at_risk_orders` in `src/services/fulfillment_router.py`.
  - **Subagent 2 (QA & Financial Auditor)**: Runs `pytest tests/test_lab04_capstone.py` and verifies that all 35 VIP orders are rerouted (`$250,000+` LTV saved, `$14,774.00` post-shipping net margin) and that `/api/v1/vendors/claim-chargebacks` recovers `$98,250.00` across the 6 breaching vendors.

---

### Step 4: Verify via CLI & Live Web Dashboard (`/browser`)

1. Run the full capstone verification script (which runs all 16 tests across Labs 01–04):
   ```bash
   ./labs/lab-04-multi-agent-capstone/verify.sh
   ```
2. Launch the FastAPI server and open `http://127.0.0.1:8000` (or ask Antigravity to inspect it via `/browser`):
   ```bash
   .venv/bin/uvicorn src.main:app --reload --port 8000
   ```
3. In the **Retail Pulse Command Center**, click:
   - **"1. Enforce 15% Margin Floor (Lab 01)"** -> Watch Margin Hold orders drop from `30` (`-$35,113.25` bleed) to `0` (`$0.00` bleed).
   - **"2. Optimize Split-Shipment Routing (Lab 04)"** -> Watch all `35` VIP Stockout orders reroute to optimal DCs/Stores (`0` at-risk orders remaining, `$14,774.00` post-shipping net margin preserved).
   - **"3. Claim OTIF Chargebacks (Lab 02/04)"** -> Watch all `6` breaching vendor contracts update to `CHARGEBACK_CLAIMED` (`$98,250.00` recovered).

---

## 4. Verification Checklist

- [ ] `./labs/lab-04-multi-agent-capstone/verify.sh` passes all **16/16 automated tests** across `test_lab01_triage.py`, `test_lab02_rules_skills.py`, `test_lab03_mcp_hooks.py`, and `test_lab04_capstone.py`.
- [ ] All 35 VIP orders in `AT_RISK_STOCKOUT` are transitioned to `REROUTED_OPTIMAL` with `$14,774.00` total post-shipping net margin.
- [ ] All 6 breaching vendor contracts are transitioned to `CHARGEBACK_CLAIMED` with `$98,250.00` in claimed penalties.

> Need to apply the verified capstone solution directly? Run `./labs/lab-04-multi-agent-capstone/apply_solution.sh`.
