# Lab 04 Prompt Playbook: Google ADK, A2A Protocol, Omnichannel Routing & Gemini Enterprise Deployment

Copy and paste these prompts into **Google Antigravity** as you complete the Lab 04 Capstone. Each phase includes prompts for both the **Technical Track** and the **Commercial / Executive Track**.

---

## Phase 1: Discovery & Multi-Agent Planning (`/plan` & `/boost`)

### Prompt 1A — Technical Track: Deep Architectural Plan for Routing + ADK + A2A (`/plan`)
```text
/plan Read @src/services/fulfillment_router.py, @src/agents/adk_a2a_orchestrator.py, @adk_agents/retail_pulse/agent.py, @src/main.py, and @tests/test_lab04_capstone.py.
Create a step-by-step implementation plan to complete our Lab 04 Capstone:
1. In `src/services/fulfillment_router.py`, implement `evaluate_candidates` and `optimize_at_risk_orders` to rank nodes with `true_atp >= qty` by `(-post_shipping_net_margin_usd, shipping_cost_usd, 0 if location_type == 'DC' else 1)` and reroute all 35 `AT_RISK_STOCKOUT` VIP orders to `REROUTED_OPTIMAL`.
2. In `src/agents/adk_a2a_orchestrator.py`, implement:
   - `WMSInventoryATPAgent.execute(conn, dry_run)` (True ATP audit + optimal split-shipment routing + `A2AAgentHandoff` to `merchandising_margin_agent`)
   - `MerchandisingMarginOTIFAgent.execute(conn, wms_handoff, dry_run)` (15% gross margin floor enforcement + vendor OTIF chargeback recovery)
   - `RetailPulseOrchestratorAgent.run_orchestration(conn, prompt, dry_run, session_id)` and `build_adk_agent_hierarchy()` using `google.adk.agents.LlmAgent` and `SequentialAgent`
   - `build_a2a_agent_card(base_url)` and `handle_a2a_jsonrpc(conn, rpc_request, base_url)` for `GET /.well-known/agent.json` and `POST /api/v1/a2a` (`tasks/send` and `message/send`).
```

### Prompt 1B — Commercial / Operations Track: Trade-Off & Multi-Agent Governance Analysis (`/boost`)
```text
/boost Read @src/services/fulfillment_router.py, @src/agents/adk_a2a_orchestrator.py, and @tests/test_lab04_capstone.py.
From a retail omnichannel profitability perspective, analyze why separating responsibilities between a Technical `WMSInventoryATPAgent` (True ATP & DC-first post-shipping margin routing) and a Commercial `MerchandisingMarginOTIFAgent` (15% gross margin floor & vendor OTIF debit memos) connected via the A2A Protocol prevents both negative-margin order bleed and VIP stockout cancellations. Then implement both modules so all 20 workshop tests pass.
```

---

## Phase 2: Multi-Agent Execution (`/teamwork` & Subagents)

### Prompt 2A — Parallel Subagent Orchestration (`/teamwork`)
```text
/teamwork Coordinate three specialized workstreams to complete our Lab 04 Capstone:
1. Omnichannel Routing Engineer: Implement `evaluate_candidates` and `optimize_at_risk_orders` in @src/services/fulfillment_router.py so all 35 `AT_RISK_STOCKOUT` VIP orders are rerouted to the highest post-shipping net margin node with sufficient True ATP.
2. ADK & A2A Systems Architect: Implement `WMSInventoryATPAgent`, `MerchandisingMarginOTIFAgent`, `RetailPulseOrchestratorAgent`, `build_a2a_agent_card`, and `handle_a2a_jsonrpc` in @src/agents/adk_a2a_orchestrator.py.
3. QA, ADK Web & Cloud Run Auditor: Run `./labs/lab-04-multi-agent-capstone/verify.sh` to validate all 20 tests across Labs 01-04, verify `./scripts/run_adk_web.sh --dry-run` and `./labs/lab-04-multi-agent-capstone/deploy_gcp.sh --dry-run`, and produce an executive summary table of the financial recovery.
```

---

## Phase 3: Inline Edit (`Cmd+I` / `Ctrl+I`)

Open `src/services/fulfillment_router.py`, select `evaluate_candidates` and `optimize_at_risk_orders`, press `Cmd+I` (macOS) or `Ctrl+I` (Windows/Linux), and enter:

```text
Implement `evaluate_candidates` using `calculate_node_atp` to filter nodes with `true_atp >= qty`, compute `post_shipping_net_margin_usd = round((effective_unit_price_usd - unit_cost_usd) * qty - shipping_cost_usd, 2)`, and sort by `(-post_shipping_net_margin_usd, shipping_cost_usd, 0 if location_type == 'DC' else 1)`. Then implement `optimize_at_risk_orders` to reroute `AT_RISK_STOCKOUT` orders (ordered by `customer_ltv_usd DESC, order_id ASC`) to `candidates[0]`, updating `omnichannel_orders` (`status='REROUTED_OPTIMAL'`) and decrementing `wms_inventory.on_hand_qty` when `not dry_run`.
```

---

## Phase 4: Local Interactive Testing with `adk web` & `/browser`

### Prompt 4A — Test Multi-Agent Hierarchy Locally in ADK Web UI (`adk web`)
```text
Validate our local Google ADK Development UI setup by running `./scripts/run_adk_web.sh --dry-run`, and inspect @adk_agents/retail_pulse/agent.py to confirm how `root_agent` (`retail_pulse_root_agent`) delegates across `wms_inventory_agent`, `merchandising_margin_agent`, and `a2a_bridge_agent`.
```

### Prompt 4B — End-to-End Browser Verification of the Retail Pulse Command Center (`/browser`)
```text
/browser Start the FastAPI server (`uvicorn src.main:app --port 8000`) if it is not already running, open `http://127.0.0.1:8000`, and verify:
1. The header displays the Tryolabs logo ("Delivered by Tryolabs") and the Retail Pulse Command Center KPIs.
2. Click "1. Enforce 15% Margin Floor (Lab 01)", "2. Optimize Split-Shipment Routing (Lab 04)", and "3. Claim OTIF Chargebacks (Lab 02/04)".
3. Confirm that Margin Hold Orders = 0, VIP Stockout Risk = 0, and all 6 breaching vendor contracts show `CHARGEBACK_CLAIMED` totaling $98,250.00.
4. Also fetch `http://127.0.0.1:8000/.well-known/agent.json` to inspect the live A2A Agent Card.
```

---

## Phase 5: Cloud Run + Terraform Deployment & Gemini Enterprise Registration

### Prompt 5 — Validate Terraform Infrastructure & Gemini Enterprise A2A Registration
```text
Read @infra/terraform/main.tf, @deploy/deploy_gcp.sh, and @deploy/register_gemini_enterprise_agent.sh.
Run `./labs/lab-04-multi-agent-capstone/deploy_gcp.sh --dry-run --project-id retail-pulse-prod --region us-central1 --gemini-app-id retail-pulse-ge-app` and explain each step of the deployment pipeline:
1. Building the container image with Cloud Build & Artifact Registry
2. Provisioning Cloud Run v2, least-privilege IAM Service Account, and Vertex AI bindings with Terraform
3. Registering the Cloud Run A2A Agent Card (`/.well-known/agent.json` & `/api/v1/a2a`) in Gemini Enterprise (Discovery Engine).
```
