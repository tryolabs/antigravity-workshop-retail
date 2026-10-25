<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Lab 04 Prompt Playbook: Google ADK, A2A Protocol, Omnichannel Routing & Gemini Enterprise Deployment

> **Language / Idioma:** [English](./PROMPTS.md) | [Español](./PROMPTS.es.md) • **Lab Guide:** [README.md](./README.md) | [README.es.md](./README.es.md) • **PDF:** [EN](./LAB_04_INSTRUCTIONS_EN.pdf) | [ES](./LAB_04_INSTRUCTIONS_ES.pdf)

Copy and paste these prompts into **Google Antigravity** as you complete the Lab 04 Capstone. Each phase includes prompts for both the **Technical Track** and the **Commercial / Executive Track**.

---

## Phase 1: Discovery & Multi-Agent Planning (`/plan` & `/boost`)

### Prompt 1A — Technical Track: Deep Architectural Plan for Routing + ADK + A2A (`/plan`)
```text
/plan Read @src/services/fulfillment_router.py, @src/agents/adk_a2a_orchestrator.py, @adk_agents/retail_pulse/agent.py, @src/main.py, and @tests/test_lab04_capstone.py.
Create a step-by-step implementation plan to complete our Lab 04 Capstone:
1. In `src/services/fulfillment_router.py`, implement `optimize_at_risk_order_routing` and `claim_vendor_otif_chargebacks` to rank eligible nodes (`true_atp >= qty`) by `(-post_shipping_margin_usd, 0 if location_type == 'DC' else 1, -true_atp)`, reroute all 35 `AT_RISK_STOCKOUT` VIP orders to `REROUTED_SAVED` (protecting $749,300.00 in VIP LTV), and claim $98,250.00 across the 6 breaching vendor OTIF contracts (`CHARGEBACK_CLAIMED`).
2. In `src/agents/adk_a2a_orchestrator.py`, implement:
   - `WMSInventoryATPAgent.execute(task_payload)` (True ATP network summary + optimal split-shipment rerouting + handoff recommendation)
   - `MerchandisingMarginOTIFAgent.execute(task_payload, wms_routing_output)` (15% gross margin floor remediation + vendor OTIF chargeback recovery)
   - `RetailPulseOrchestratorAgent.run_multi_agent_workflow(prompt, skill_id, metadata)` coordinating `WMSInventoryATPAgent` -> `MerchandisingMarginOTIFAgent` with Google ADK metadata
   - `get_a2a_agent_card(base_url)` and `handle_a2a_jsonrpc(payload, db_path)` for `GET /.well-known/agent.json` and `POST /api/v1/a2a/tasks/send` (`tasks/send`, `message/send`, and `tasks/get`).
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
1. Omnichannel Routing Engineer: Implement `optimize_at_risk_order_routing` and `claim_vendor_otif_chargebacks` in @src/services/fulfillment_router.py so all 35 `AT_RISK_STOCKOUT` VIP orders are rerouted to `REROUTED_SAVED` ($749,300.00 VIP LTV protected) and all 6 breaching supplier contracts transition to `CHARGEBACK_CLAIMED` ($98,250.00 recovered).
2. ADK & A2A Systems Architect: Implement `WMSInventoryATPAgent`, `MerchandisingMarginOTIFAgent`, `RetailPulseOrchestratorAgent`, `get_a2a_agent_card`, and `handle_a2a_jsonrpc` in @src/agents/adk_a2a_orchestrator.py.
3. QA, ADK Web & Cloud Run Auditor: Run `./labs/lab-04-multi-agent-capstone/verify.sh` to validate all 20 tests across Labs 01-04, verify `./scripts/run_adk_web.sh --check` and `./labs/lab-04-multi-agent-capstone/deploy_gcp.sh --dry-run`, and produce an executive summary table of the financial recovery.
```

---

## Phase 3: Inline Edit (`Cmd+I` / `Ctrl+I`)

Open `src/services/fulfillment_router.py`, select `optimize_at_risk_order_routing` and `claim_vendor_otif_chargebacks`, press `Cmd+I` (macOS) or `Ctrl+I` (Windows/Linux), and enter:

```text
Implement `optimize_at_risk_order_routing` using `evaluate_location_atp` to filter candidate nodes with `can_fulfill == True`, compute `post_shipping_margin_usd = round((unit_price - unit_cost) * qty - shipping_cost, 2)`, sort by `(-post_shipping_margin_usd, 0 if location_type == 'DC' else 1, -true_atp)`, and update `omnichannel_orders` (`status='REROUTED_SAVED'`) when `persist_changes=True`. Then implement `claim_vendor_otif_chargebacks` using `audit_all_vendor_otif_contracts(only_breaching=True)` to transition breaching contracts to `status='CHARGEBACK_CLAIMED'`.
```

---

## Phase 4: Local Interactive Testing with `adk web` & `/browser`

### Prompt 4A — Test Multi-Agent Hierarchy Locally in ADK Web UI (`adk web`)
```text
Validate our local Google ADK Development UI setup by running `./scripts/run_adk_web.sh --check`, and inspect @adk_agents/retail_pulse/agent.py to confirm how `root_agent` (`retail_pulse_orchestrator`) delegates across `wms_inventory_atp_agent` and `merchandising_margin_otif_agent`.
```

### Prompt 4B — End-to-End Browser Verification of the Retail Pulse Command Center (`/browser`)
```text
/browser Start the FastAPI server (`./.venv/bin/uvicorn src.main:app --host 127.0.0.1 --port 8002`) if it is not already running, open `http://localhost:8002`, and verify:
1. The header displays the Tryolabs logo ("Delivered by Tryolabs") and the Retail Pulse Command Center KPIs.
2. Execute the remediation actions (`POST /api/v1/remediate/margins`, `POST /api/v1/remediate/routing`, or `POST /api/v1/a2a/tasks/send`).
3. Confirm that Margin Hold Orders = 0, VIP Stockout Risk = 0 ($749,300.00 VIP LTV protected), and all 6 breaching vendor contracts show `CHARGEBACK_CLAIMED` totaling $98,250.00.
4. Also fetch `http://localhost:8002/.well-known/agent.json` to inspect the live A2A Agent Card.
```

---

## Phase 5: Cloud Run + Terraform Deployment & Gemini Enterprise Registration

### Prompt 5 — Validate Terraform Infrastructure & Gemini Enterprise A2A Registration
```text
Read @infra/terraform/main.tf, @deploy/deploy_gcp.sh, and @deploy/register_gemini_enterprise_agent.sh.
Run `./labs/lab-04-multi-agent-capstone/deploy_gcp.sh --dry-run --project-id retail-pulse-prod --region us-central1 --gemini-app-id retail-pulse-ge-app` and explain each step of the deployment pipeline:
1. Building the container image with Cloud Build & Artifact Registry
2. Provisioning Cloud Run v2, least-privilege IAM Service Account, and Vertex AI bindings with Terraform
3. Registering the Cloud Run A2A Agent Card (`/.well-known/agent.json` & `/api/v1/a2a/tasks/send`) in Gemini Enterprise (Discovery Engine).
```
