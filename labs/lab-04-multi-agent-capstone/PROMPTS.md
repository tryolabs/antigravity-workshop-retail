# Lab 04 Prompt Playbook: Multi-Agent Omnichannel Routing & Executive Command Center

Copy and paste these prompts into **Google Antigravity** as you complete the Lab 04 Capstone. Each phase includes prompts for both the **Technical Track** and the **Commercial / Executive Track**.

---

## Phase 1: Discovery & Multi-Agent Planning (`/plan` & `/boost`)

### Prompt 1A — Technical Track: Deep Architectural Plan (`/plan`)
```text
/plan Read @src/services/fulfillment_router.py, @src/services/inventory_atp.py, @src/main.py, and @tests/test_lab04_capstone.py.
Create a step-by-step implementation plan for `evaluate_candidates` and `optimize_at_risk_orders` in `src/services/fulfillment_router.py`:
1. Filter `wms_inventory` nodes where `calculate_node_atp(dict(row)) >= qty`.
2. Compute `gross_margin_usd = (effective_unit_price_usd - unit_cost_usd) * qty` and `post_shipping_net_margin_usd = round(gross_margin_usd - shipping_cost_usd, 2)`.
3. Sort eligible candidates by `(-post_shipping_net_margin_usd, shipping_cost_usd, 0 if location_type == 'DC' else 1)`.
4. In `optimize_at_risk_orders(conn, dry_run=False)`, iterate over all `AT_RISK_STOCKOUT` orders ordered by `customer_ltv_usd DESC, order_id ASC`, reroute each to the top candidate (`status = 'REROUTED_OPTIMAL'`), decrement `on_hand_qty` at the winning node when `not dry_run`, and return the summary metrics expected by `tests/test_lab04_capstone.py`.
```

### Prompt 1B — Commercial / Operations Track: Trade-Off Analysis (`/boost`)
```text
/boost Read @src/services/fulfillment_router.py and @tests/test_lab04_capstone.py.
From a retail omnichannel profitability perspective, analyze why ranking fulfillment nodes by Post-Shipping Net Margin (`gross_margin_usd - shipping_zone_cost_usd`) with a tie-breaker favoring regional Distribution Centers (`DC`) over ship-from-store (`STORE`) protects both unit economics and flagship store walk-in availability. Then implement the routing engine in `src/services/fulfillment_router.py`.
```

---

## Phase 2: Multi-Agent Execution (`/teamwork` & Subagents)

### Prompt 2A — Parallel Subagent Orchestration (`/teamwork`)
```text
/teamwork Coordinate two specialized workstreams to complete our Lab 04 Capstone:
1. Fulfillment Routing Engineer: Implement `evaluate_candidates` and `optimize_at_risk_orders` in @src/services/fulfillment_router.py so that all 35 `AT_RISK_STOCKOUT` VIP orders are rerouted to the highest post-shipping net margin node with sufficient True ATP.
2. QA & Commercial Auditor: Run `./labs/lab-04-multi-agent-capstone/verify.sh` to validate all 16 tests across Labs 01-04, and produce an executive summary table showing:
   - Total Margin Bleed eliminated (Lab 01)
   - Total VIP Customer LTV saved and Post-Shipping Net Margin preserved across the 35 rerouted VIP orders (Lab 04)
   - Total Vendor OTIF Chargebacks recovered across the 6 breaching vendors (Lab 02/04)
```

---

## Phase 3: Inline Edit (`Cmd+I` / `Ctrl+I`)

Open `src/services/fulfillment_router.py`, select `evaluate_candidates` and `optimize_at_risk_orders`, press `Cmd+I` (macOS) or `Ctrl+I` (Windows/Linux), and enter:

```text
Implement `evaluate_candidates` using `calculate_node_atp` to filter nodes with `true_atp >= qty`, compute `post_shipping_net_margin_usd = round((effective_unit_price_usd - unit_cost_usd) * qty - shipping_cost_usd, 2)`, and sort by `(-post_shipping_net_margin_usd, shipping_cost_usd, 0 if location_type == 'DC' else 1)`. Then implement `optimize_at_risk_orders` to reroute `AT_RISK_STOCKOUT` orders (ordered by `customer_ltv_usd DESC, order_id ASC`) to `candidates[0]`, updating `omnichannel_orders` (`status='REROUTED_OPTIMAL'`) and decrementing `wms_inventory.on_hand_qty` when `not dry_run`.
```

---

## Phase 4: Visual Command Center Verification (`/browser`)

### Prompt 4 — End-to-End Browser Verification of the Retail Pulse Command Center
```text
/browser Start the FastAPI server (`uvicorn src.main:app --port 8000`) if it is not already running, open `http://127.0.0.1:8000`, and verify:
1. The header displays the Tryolabs logo ("Delivered by Tryolabs") and the Retail Pulse Command Center KPIs.
2. Click "1. Enforce 15% Margin Floor (Lab 01)", "2. Optimize Split-Shipment Routing (Lab 04)", and "3. Claim OTIF Chargebacks (Lab 02/04)".
3. Confirm that Margin Hold Orders = 0, VIP Stockout Risk = 0, and all 6 breaching vendor contracts show `CHARGEBACK_CLAIMED` totaling $98,250.00.
```

---

## Phase 5: Stretch Challenge — Split-Line Multi-Node Fulfillment

### Prompt 5 — Design Multi-Node Split Shipments When No Single Node Has Full Qty
```text
What if a high-quantity VIP order (e.g., 25 units) cannot be fulfilled by any single DC or Store node alone, but can be fulfilled by splitting across two nodes (e.g., 15 units from `DC-EAST-01` + 10 units from `DC-CENTRAL-02`)?
Propose a non-breaking helper function `evaluate_split_shipment_pair(conn, sku, qty, effective_unit_price_usd)` that finds the highest net-margin 2-node split when `evaluate_candidates` returns an empty list, while ensuring combined shipping costs do not breach our 15% minimum margin floor.
```
