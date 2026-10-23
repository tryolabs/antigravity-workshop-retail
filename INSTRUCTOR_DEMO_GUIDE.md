<div align="center">
  <img src="src/static/tryolabs-logo.png" alt="Tryolabs Logo" height="44" />
  <h1>Instructor Master Run-of-Show & Live Demo Guide</h1>
  <p><strong>Google Antigravity Retail Industry Workshop — Delivered by Tryolabs</strong></p>
  <p><a href="INSTRUCTOR_DEMO_GUIDE.md"><strong>English</strong></a> | <a href="INSTRUCTOR_DEMO_GUIDE.es.md"><strong>Español</strong></a> | <a href="README.md"><strong>Main README</strong></a></p>
</div>

---

## 1. Pre-Flight Checklist (15 Minutes Before Workshop Starts)

1. **Bootstrap & Reset to Lab 01 Starter State**:
   ```bash
   ./install.sh
   ```
2. **Start the Retail Pulse Command Center (Background Terminal Tab 1)**:
   ```bash
   .venv/bin/uvicorn src.main:app --reload --port 8000
   ```
3. **Open `http://127.0.0.1:8000` in Chrome**:
   - Verify the **Tryolabs logo ("Delivered by Tryolabs")** appears in the top header.
   - Verify the 3 crisis KPIs are displayed in red/amber:
     - **Margin Hold Orders**: `30` (`-$35,113.25` Margin Bleed)
     - **VIP Stockout Risk**: `35` VIP Orders (`>$250,000` LTV Exposed)
     - **OTIF Chargeback Recovery**: `6` Breaching Vendors (`$98,250.00` Unclaimed)
4. **Know Your Instant Recovery Commands**:
   If you or any attendee ever need to jump cleanly to the start or solution of any lab:
   ```bash
   # Reset to Lab X starter state:
   ./labs/lab-01-margin-inventory-triage/install.sh
   ./labs/lab-02-rules-and-skills/install.sh
   ./labs/lab-03-mcp-and-hooks/install.sh
   ./labs/lab-04-multi-agent-capstone/install.sh

   # Apply Lab X solution & verify:
   ./labs/lab-01-margin-inventory-triage/apply_solution.sh && ./labs/lab-01-margin-inventory-triage/verify.sh
   ./labs/lab-02-rules-and-skills/apply_solution.sh       && ./labs/lab-02-rules-and-skills/verify.sh
   ./labs/lab-03-mcp-and-hooks/apply_solution.sh          && ./labs/lab-03-mcp-and-hooks/verify.sh
   ./labs/lab-04-multi-agent-capstone/apply_solution.sh   && ./labs/lab-04-multi-agent-capstone/verify.sh
   ```

---

## 2. Module-by-Module Live Demo Script (4 Hours)

### Module 0: Executive Briefing & Crisis Tour (`00:00 - 00:30`)

#### Talking Points
- Welcome attendees on behalf of **Tryolabs**. Explain that today's workshop pairs **Platform/Software Engineers** and **Commercial/Merchandising/Supply Chain Managers** around a realistic Black Friday omnichannel crisis (**Retail Pulse**).
- Show `http://127.0.0.1:8000`. Point out that the platform is bleeding `-$35,113.25` on 30 stacked-promo orders, stranding 35 `DIAMOND`/`GOLD` VIP orders (`>$250K` LTV) due to phantom BOPIS inventory, and leaving `$98,250.00` in vendor OTIF penalties on the table.
- Contrast **Editor View** (for synchronous inline edits with `Cmd+I` / `Ctrl+I`) with **Agent Manager (`Cmd+E` / `Ctrl+E`)** (for asynchronous multi-step planning, testing, and subagent delegation).

---

### Module 1: Lab 01 — Omnichannel Flash-Sale Triage (`00:30 - 01:15`)

#### Capabilities Demonstrated
- `@` Context Mentions (`@src/services/promo_pricing.py`, `@data/exports/omnichannel_orders.csv`)
- `/plan` Interactive Artifact Planning
- Inline Edit (`Cmd+I` / `Ctrl+I`)
- Autonomous Test-Driven Verification (`pytest`)

#### Live Demo Steps
1. Run `./labs/lab-01-margin-inventory-triage/verify.sh` in the terminal to show the 2 failing tests (`test_promo_pricing_enforces_minimum_margin_floor` and `test_true_atp_deducts_bopis_damaged_and_safety_stock`).
2. Paste **Prompt 1A** (Technical) or **Prompt 1B** (Commercial) from `labs/lab-01-margin-inventory-triage/PROMPTS.md` to diagnose Bug #1A and Bug #1B.
3. Paste **Prompt 2** (`/plan`) to generate a structured implementation plan artifact.
4. Highlight `calculate_stacked_promo_price` in `src/services/promo_pricing.py`, press `Cmd+I` / `Ctrl+I`, and apply the 15% margin floor (`unit_cost_usd / (1.0 - minimum_margin_pct)`).
5. Ask Antigravity to fix `calculate_node_atp` in `src/services/inventory_atp.py` (`max(0, on_hand - reserved_bopis - damaged_hold - safety_stock)`) and run `./labs/lab-01-margin-inventory-triage/verify.sh`.
6. In the browser (`http://127.0.0.1:8000`), click **"1. Enforce 15% Margin Floor (Lab 01)"** and show that Margin Hold orders drop from `30` to `0` (`$0.00` bleed)!

---

### Module 2: Lab 02 — Customizations (`GEMINI.md`, Rules & Skills) (`01:15 - 02:00`)

#### Capabilities Demonstrated
- Workspace Memory (`GEMINI.md`)
- Domain Rules (`.agents/rules/retail-standards.md`)
- Reusable Skills with YAML Frontmatter + Helper Scripts (`.agents/skills/retail-otif-margin-auditor/SKILL.md` + `scripts/run_otif_margin_audit.py`)
- `/learn` Slash Command

#### Live Demo Steps
1. Run `./labs/lab-02-rules-and-skills/install.sh` and `./labs/lab-02-rules-and-skills/verify.sh`.
2. Explain the **Antigravity Customization Hierarchy**:
   - **Always-on workspace memory**: `GEMINI.md`
   - **Targeted domain guardrails**: `.agents/rules/retail-standards.md` (GS1 Modulo-10 GTIN-14 validation, 15% margin floor, OTIF chargeback tiers: 85%–89.99% -> 3%, 80%–84.99% -> 5%, <80% -> 8%)
   - **On-demand procedural workflows**: `.agents/skills/retail-otif-margin-auditor/SKILL.md`
3. Run **Prompt 4A** from `labs/lab-02-rules-and-skills/PROMPTS.md` (or use `/learn`) to generate all three files.
4. Run `./labs/lab-02-rules-and-skills/verify.sh` and then trigger the skill with **Prompt 5B**:
   - Show the generated executive Markdown table identifying **6 breaching vendors** and **$98,250.00 in recoverable chargebacks** (`VND-APEX-01`: `$31,200`, `VND-LUXE-02`: `$14,250`, `VND-SOLAR-04`: `$24,800`, `VND-VELO-05`: `$7,600`, `VND-KINETIC-07`: `$9,900`, `VND-OMNI-09`: `$10,500`).

---

### Module 3: Lab 03 — FastMCP Server, Deterministic Hooks & Enterprise Security (`02:00 - 02:55`)

#### Capabilities Demonstrated
- FastMCP Server (`mcp_server/retail_mcp.py` & `.agents/mcp_config.json`)
- Deterministic Lifecycle Hooks (`.agents/hooks.json` & `scripts/margin_guard_hook.py` -> `data/logs/hook_compliance_audit.jsonl`)
- **Enterprise Governance Deep-Dive**: Google Cloud IAM / Cloud Audit Logs / VPC-SC + Antigravity Client Sandbox & Permission Controls

#### Live Demo Steps (Part A — MCP & Hooks)
1. Run `./labs/lab-03-mcp-and-hooks/install.sh` and `./labs/lab-03-mcp-and-hooks/verify.sh`.
2. Open `mcp_server/retail_mcp.py` and show the 2 implemented tools (`query_true_atp_inventory`, `audit_vendor_otif_contracts`) and 2 stubs (`simulate_promo_margin_guard`, `list_at_risk_vip_orders`).
3. Run **Prompt 4A** from `labs/lab-03-mcp-and-hooks/PROMPTS.md` to implement both MCP tools and create `.agents/mcp_config.json` and `.agents/hooks.json`.
4. **Live Adversarial Hook Demo**:
   Run the following command in the terminal to simulate an agent or user trying to disable the 15% margin floor (`enforce_floor=False`):
   ```bash
   echo '{"tool_name":"edit_file","tool_input":{"Path":"src/services/promo_pricing.py","Replacement":"enforce_floor=False"}}' | .venv/bin/python scripts/margin_guard_hook.py
   ```
   Show the red `[MARGIN_GUARD_HOOK BLOCKED]` message (exit code `2`) and inspect the immutable compliance log:
   ```bash
   cat data/logs/hook_compliance_audit.jsonl
   ```
5. Run `./labs/lab-03-mcp-and-hooks/verify.sh` to confirm all 5/5 tests pass.

#### Live Demo Steps (Part B — Enterprise Security & Governance Walkthrough)
Walk the audience through the two enterprise governance layers documented in `labs/lab-03-mcp-and-hooks/README.md`:

1. **Layer 1: Google Cloud & Gemini Enterprise Admin Plane**:
   - **Identity & Seat Management**: Show how enterprise admins grant `roles/cloudaicompanion.user` in Google Cloud IAM mapped to Cloud Identity / Okta / Entra ID groups (`retail-engineering@`, `retail-merchandising@`).
   - **Cloud Audit Logging (`cloudaicompanion.googleapis.com`)**: Share this exact Google Cloud Logging filter that enterprise SecOps teams use to audit Gemini Enterprise activity in BigQuery / Chronicle SIEM:
     ```text
     protoPayload.serviceName="cloudaicompanion.googleapis.com"
     AND logName=("projects/YOUR_GCP_PROJECT/logs/cloudaudit.googleapis.com%2Factivity"
       OR "projects/YOUR_GCP_PROJECT/logs/cloudaudit.googleapis.com%2Fdata_access")
     ```
   - **Zero Data Retention & No Foundation Model Training**: Emphasize that wholesale costs, vendor SLA contracts, and proprietary source code are never retained to train Google models.
   - **VPC Service Controls (VPC-SC) & Regional Endpoints**: Explain how `cloudaicompanion.googleapis.com` operates inside a VPC-SC perimeter alongside BigQuery and Cloud SQL.

2. **Layer 2: Antigravity Client & Workspace Security Controls**:
   - Open the Antigravity Settings panel and demonstrate:
     - **Tool Execution Policy**: `strict`, `request-review`, `proceed-in-sandbox`, `always-proceed`.
     - **Terminal Sandbox & Network Isolation**: OS-level sandboxing and outbound network toggle.
     - **Non-Workspace File Access**: Blocking reads/writes outside `/antigravity-workshop-retail`.
     - **Command Allowlist / Denylist & Browser Allowlist**: Allowlisting `.venv/bin/python -m pytest` and restricting `/browser` to `http://127.0.0.1:8000`.
     - **Deterministic Hooks (`.agents/hooks.json`)**: Pre-execution policy enforcement writing to `data/logs/hook_compliance_audit.jsonl`.

---

### Module 4: Lab 04 — Multi-Agent Capstone: Smart Split-Shipment Routing (`02:55 - 03:45`)

#### Capabilities Demonstrated
- `/plan` & `/boost` for multi-constraint optimization design
- `/teamwork` & Subagent Orchestration (`invoke_subagent`)
- `/browser` Live Web UI Verification

#### Live Demo Steps
1. Run `./labs/lab-04-multi-agent-capstone/install.sh` and `./labs/lab-04-multi-agent-capstone/verify.sh`.
2. Show `src/services/fulfillment_router.py` where `evaluate_candidates` and `optimize_at_risk_orders` raise `NotImplementedError`.
3. Paste **Prompt 1A (`/plan`)** or **Prompt 2A (`/teamwork`)** from `labs/lab-04-multi-agent-capstone/PROMPTS.md` to implement the routing engine and run the full test suite.
4. Run `./labs/lab-04-multi-agent-capstone/verify.sh` and celebrate **16/16 passing tests** across Labs 01, 02, 03, and 04!
5. Return to `http://127.0.0.1:8000` (or invoke **Prompt 4 (`/browser`)**):
   - Click **"1. Enforce 15% Margin Floor (Lab 01)"** -> `0` Margin Hold orders (`$0.00` bleed).
   - Click **"2. Optimize Split-Shipment Routing (Lab 04)"** -> All `35` VIP Stockout orders rerouted (`$250,000+` LTV saved, `$14,774.00` post-shipping net margin preserved).
   - Click **"3. Claim OTIF Chargebacks (Lab 02/04)"** -> All `6` breaching vendor contracts marked `CHARGEBACK_CLAIMED` (`$98,250.00` recovered).

---

## 3. Summary of Verified Financial & Operational Metrics

Use this reference table during executive Q&A to explain the deterministic numbers built into `data/seed_retail_data.py`:

| Metric | Initial Crisis State (Starter) | Post-Remediation State (Solution) | Verified By |
| :--- | :--- | :--- | :--- |
| **Margin Hold Orders (`MARGIN_HOLD`)** | `30` orders (`-$35,113.25` negative margin bleed) | `0` orders (`$0.00` bleed; clamped to `>= 15%` gross margin floor) | `tests/test_lab01_triage.py` |
| **VIP Stockout Orders (`AT_RISK_STOCKOUT`)** | `35` VIP (`DIAMOND`/`GOLD`) orders (`>$250,000` Customer LTV exposed) | `0` at-risk orders (`35` rerouted to `REROUTED_OPTIMAL` with `$14,774.00` post-shipping net margin) | `tests/test_lab04_capstone.py` |
| **Vendor OTIF Breaches (`BREACH_DETECTED`)** | `6` breaching contracts (`$98,250.00` unclaimed penalties across `10` vendors) | `6` contracts transitioned to `CHARGEBACK_CLAIMED` (`$98,250.00` recovered) | `tests/test_lab02_rules_skills.py` & `tests/test_lab04_capstone.py` |
| **PreToolUse Hook Compliance Audit** | Unprotected against `enforce_floor=False` edits | Deterministic exit code `2` block + JSONL audit log in `data/logs/hook_compliance_audit.jsonl` | `tests/test_lab03_mcp_hooks.py` |
