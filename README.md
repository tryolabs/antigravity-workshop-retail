<div align="center">
  <img src="src/static/tryolabs-logo.png" alt="Tryolabs Logo" height="48" />
  <h1>Retail Pulse — Google Antigravity Hands-On Workshop</h1>
  <p><strong>Omnichannel Order, Inventory Sync & Commercial Margin / Vendor Contract Intelligence Platform</strong></p>
  <p><em>Delivered by <strong>Tryolabs</strong> | 4-Hour Enterprise Retail & Omnichannel Commerce Workshop</em></p>
  <p><a href="README.md"><strong>English</strong></a> | <a href="README.es.md"><strong>Español</strong></a> | <a href="INSTRUCTOR_DEMO_GUIDE.md"><strong>Instructor Demo Guide (EN)</strong></a> | <a href="INSTRUCTOR_DEMO_GUIDE.es.md"><strong>Guía del Instructor (ES)</strong></a></p>
</div>

---

## 1. Executive Summary & Dual-Track Design

Welcome to the **Google Antigravity Retail Industry Workshop**, designed and delivered by **Tryolabs**.

During peak seasonal events (Flash Sales / Black Friday), retail enterprises face an intersecting crisis across **Platform Engineering** and **Commercial / Merchandising Operations**:
1. **Unclamped Promotional Discount Stacking (`-$35,113.25` Margin Bleed)**: Campaign promo codes stack multiplicatively with loyalty tier discounts without enforcing the 15% gross margin floor (`minimum_margin_pct`), selling flagship items below wholesale unit cost.
2. **Phantom Inventory & Stockout Risk (`$250,000+` VIP LTV Exposed)**: The Available-to-Promise (`ATP`) engine checks raw `on_hand_qty` while ignoring `reserved_bopis_qty`, `damaged_hold_qty`, and `safety_stock_qty`, stranding **35 VIP (`DIAMOND`/`GOLD`) orders** in `AT_RISK_STOCKOUT`.
3. **Unclaimed Vendor OTIF Penalties (`$98,250.00` Recoverable Chargebacks)**: 6 of 10 strategic suppliers are breaching contractual On-Time In-Full (`OTIF`) SLAs (`actual_otif_pct < otif_target_pct`), leaving nearly `$100K` in contractual chargebacks unclaimed.

This repository supports **both Technical Engineers and Commercial/Operations Managers** working side by side:
- **Technical Track (Software, Data & Platform Engineers)**: Debug Python/FastAPI microservices, write `pytest` suites, build FastMCP tools (`mcp_server/retail_mcp.py`), enforce deterministic `PreToolUse` hooks (`scripts/margin_guard_hook.py`), and orchestrate multi-agent fulfillment routing (`src/services/fulfillment_router.py`).
- **Commercial Track (Merchandising, Category Management & Supply Chain Operations)**: Audit CSV exports (`data/exports/`), encode corporate margin & OTIF rules (`GEMINI.md`, `.agents/rules/retail-standards.md`), create reusable executive audit skills (`.agents/skills/`), query live retail databases through natural-language MCP tools, and validate KPIs in the live **Retail Pulse Command Center** (`http://127.0.0.1:8000`).

---

## 2. System Architecture

```
+---------------------------------------------------------------------------------------------------+
|                           GOOGLE ANTIGRAVITY IDE & AGENT RUNTIME                                  |
|  - Slash Commands: /plan, /boost, /teamwork, /browser, /learn, /compact, /goal                    |
|  - Customizations: GEMINI.md | .agents/rules/ | .agents/skills/ | .agents/hooks.json              |
+------------------------------------+-----------------------------------+--------------------------+
                                     |                                   |
                   Stdio FastMCP     |                                   | HTTP / REST & /browser
                                     v                                   v
+------------------------------------+-----------------------------------+--------------------------+
|  MCP SERVER (mcp_server/retail_mcp.py)       |  FASTAPI APP & COMMAND CENTER (src/main.py)        |
|  - query_true_atp_inventory                  |  - Web UI: src/static/index.html (Tryolabs Brand)  |
|  - audit_vendor_otif_contracts               |  - Promo Pricing: src/services/promo_pricing.py    |
|  - simulate_promo_margin_guard               |  - True ATP Sync: src/services/inventory_atp.py    |
|  - list_at_risk_vip_orders                   |  - OTIF Auditor:  src/services/vendor_otif_auditor |
|                                              |  - Smart Router:  src/services/fulfillment_router  |
+------------------------------------+---------+-------------------------+--------------------------+
                                     |                                   |
                                     +-----------------+-----------------+
                                                       |
                                                       v
+---------------------------------------------------------------------------------------------------+
|                           DETERMINISTIC RETAIL DATA LAYER (data/)                                 |
|  - SQLite DB: data/retail_pulse.db (vendor_contracts, wms_inventory, promo_campaigns, orders)     |
|  - Commercial CSV Exports: data/exports/{vendor_contracts,wms_inventory,omnichannel_orders}.csv   |
|  - Webhook & Compliance Logs: data/logs/{pos_wms_webhooks.jsonl, hook_compliance_audit.jsonl}     |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. 4-Hour Workshop Curriculum & Lab Matrix

| Module | Duration | Focus Area & Antigravity Capabilities | Lab Guide & Prompt Playbook | Automation Scripts |
| :--- | :--- | :--- | :--- | :--- |
| **Setup & Briefing** | `00:00 - 00:30` | Environment setup, Retail Pulse Command Center tour, Antigravity IDE + Agent Manager overview | [Instructor Guide (EN)](INSTRUCTOR_DEMO_GUIDE.md) / [ES](INSTRUCTOR_DEMO_GUIDE.es.md) | `./install.sh` (or `./install.ps1`) |
| **Lab 01** | `00:30 - 01:15` | **Omnichannel Flash-Sale Triage**: Context `@` mentions, `/plan`, Inline Edit (`Cmd+I`), fixing Promo Margin Stacking (Bug #1A) & Phantom ATP Inventory (Bug #1B) | [Lab 01 Guide (EN)](labs/lab-01-margin-inventory-triage/README.md) \| [ES](labs/lab-01-margin-inventory-triage/README.es.md)<br>[Prompts (EN)](labs/lab-01-margin-inventory-triage/PROMPTS.md) \| [ES](labs/lab-01-margin-inventory-triage/PROMPTS.es.md) | `labs/lab-01-margin-inventory-triage/{install.sh,verify.sh,apply_solution.sh}` |
| **Lab 02** | `01:15 - 02:00` | **Customizations (`GEMINI.md`, Rules & Skills)**: Encoding GS1 GTIN-14, 15% margin floor & OTIF standards in `.agents/rules/retail-standards.md` and building `.agents/skills/retail-otif-margin-auditor/SKILL.md` | [Lab 02 Guide (EN)](labs/lab-02-rules-and-skills/README.md) \| [ES](labs/lab-02-rules-and-skills/README.es.md)<br>[Prompts (EN)](labs/lab-02-rules-and-skills/PROMPTS.md) \| [ES](labs/lab-02-rules-and-skills/PROMPTS.es.md) | `labs/lab-02-rules-and-skills/{install.sh,verify.sh,apply_solution.sh}` |
| **Lab 03** | `02:00 - 02:55` | **FastMCP Server, Deterministic Hooks & Enterprise Governance**: Building `mcp_server/retail_mcp.py`, `.agents/mcp_config.json`, `PreToolUse` hook (`scripts/margin_guard_hook.py`), and Gemini Enterprise / Cloud Security | [Lab 03 Guide (EN)](labs/lab-03-mcp-and-hooks/README.md) \| [ES](labs/lab-03-mcp-and-hooks/README.es.md)<br>[Prompts (EN)](labs/lab-03-mcp-and-hooks/PROMPTS.md) \| [ES](labs/lab-03-mcp-and-hooks/PROMPTS.es.md) | `labs/lab-03-mcp-and-hooks/{install.sh,verify.sh,apply_solution.sh}` |
| **Lab 04** | `02:55 - 03:45` | **Multi-Agent Capstone**: Orchestrating `/plan`, `/boost`, `/teamwork`, and `/browser` to build Smart Split-Shipment Routing (`src/services/fulfillment_router.py`) and save 35 VIP orders (`$14,774` net margin) | [Lab 04 Guide (EN)](labs/lab-04-multi-agent-capstone/README.md) \| [ES](labs/lab-04-multi-agent-capstone/README.es.md)<br>[Prompts (EN)](labs/lab-04-multi-agent-capstone/PROMPTS.md) \| [ES](labs/lab-04-multi-agent-capstone/PROMPTS.es.md) | `labs/lab-04-multi-agent-capstone/{install.sh,verify.sh,apply_solution.sh}` |
| **Wrap-Up** | `03:45 - 04:00` | Production rollout patterns, Q&A with Tryolabs solutions architects | [Instructor Guide (EN)](INSTRUCTOR_DEMO_GUIDE.md) | `./labs/lab-04-multi-agent-capstone/verify.sh` |

---

## 4. Quickstart Instructions

### Prerequisites
- **Python 3.10+**
- **Google Antigravity** (Desktop IDE or `agy` CLI)
- macOS, Linux, or Windows (PowerShell)

### 1. Bootstrap the Workshop Environment
Run the root installer to create the `.venv` virtual environment, install dependencies (`fastapi`, `uvicorn`, `pydantic`, `pytest`, `httpx`, `mcp`), seed the deterministic retail database (`data/retail_pulse.db`), generate CSV exports (`data/exports/`), and initialize **Lab 01 Starter State**:

**macOS / Linux:**
```bash
./install.sh
```

**Windows (PowerShell):**
```powershell
.\install.ps1
```

### 2. Launch the Live Retail Pulse Command Center
Start the FastAPI server and open `http://127.0.0.1:8000` in your browser:

```bash
.venv/bin/uvicorn src.main:app --reload --port 8000
```

You will see the **Retail Pulse Command Center** (branded with **Delivered by Tryolabs**) displaying the initial crisis metrics:
- **Margin Hold Orders**: `30` orders (`-$35,113.25` Margin Bleed)
- **VIP Stockout Risk**: `35` VIP orders (`$250,000+` Customer LTV exposed)
- **OTIF Chargeback Recovery**: `6` breaching vendors (`$98,250.00` recoverable penalties)

### 3. Run Lab Installers, Verifiers & Solution Scripts
Every lab folder (`labs/lab-01-*` through `labs/lab-04-*`) is completely self-contained and includes:
- `./labs/<lab-name>/install.sh` — Resets the workspace to the exact starter state for that lab (automatically applying prerequisites from earlier labs).
- `./labs/<lab-name>/verify.sh` — Runs the automated `pytest` verification suite for that lab.
- `./labs/<lab-name>/apply_solution.sh` — Instantly applies the reference solution for that lab.

---

## 5. Enterprise Security, Privacy & Governance (Google Cloud + Antigravity)

Enterprise retail adopters require defense-in-depth across cloud identity, data privacy, network perimeters, and local agent execution. This workshop demonstrates the **two-layer governance model** covered in depth in [Lab 03](labs/lab-03-mcp-and-hooks/README.md):

### Layer 1: Google Cloud & Gemini Enterprise Governance (Cloud Admin Plane)
- **IAM & Seat Assignment**: Provision access via Google Cloud IAM role `roles/cloudaicompanion.user` federated with **Cloud Identity, Okta, or Microsoft Entra ID (Azure AD)** SSO groups.
- **Cloud Audit Logs (`cloudaicompanion.googleapis.com`)**: Enable Admin Activity and Data Access logs in **Google Cloud Logging** to capture an immutable audit trail of every API invocation, user identity, timestamp, and project metadata, with optional routing via Log Sinks to BigQuery or Chronicle SIEM.
- **Zero Data Retention & No Model Training**: Customer prompts, SQL schemas, wholesale pricing tables, vendor SLA contracts, and source code are **never used to train Google foundation models** and remain strictly isolated within your enterprise boundary.
- **VPC Service Controls (VPC-SC) & Regional Endpoints**: Protect `cloudaicompanion.googleapis.com` inside a VPC-SC perimeter alongside BigQuery and Cloud SQL to prevent data exfiltration, backed by Google Cloud copyright indemnification.

### Layer 2: Antigravity Client & Workspace Security Controls (Local Execution Plane)
- **Tool Execution Policy**: Configure `strict`, `request-review`, `proceed-in-sandbox`, or `always-proceed` to govern when shell commands or file writes require human approval.
- **Terminal Sandbox & Network Isolation**: Enforce OS-level sandboxing (`sandbox-exec` on macOS / container namespaces on Linux) and restrict outbound internet access.
- **Non-Workspace File Access Protection**: Prevent agents from reading or modifying files outside the `/antigravity-workshop-retail` workspace boundary (protecting `~/.ssh`, `~/.aws`, and host credentials).
- **Command Allowlist / Denylist & Browser Allowlist**: Allowlist safe test runners (`.venv/bin/python -m pytest`) while blocking destructive shell commands (`rm -rf`, `curl`) and restricting `/browser` to `http://127.0.0.1:8000`.
- **Deterministic Lifecycle Hooks (`.agents/hooks.json`)**: Execute deterministic pre-tool validation (`scripts/margin_guard_hook.py`) before any file modification occurs, blocking 15% margin floor bypasses with exit code `2` and recording every decision to `data/logs/hook_compliance_audit.jsonl`.

---

## 6. Repository Structure

```text
antigravity-workshop-retail/
├── README.md                                 # English Workshop Guide
├── README.es.md                              # Spanish Workshop Guide
├── INSTRUCTOR_DEMO_GUIDE.md                  # English Step-by-Step Instructor Demo Script
├── INSTRUCTOR_DEMO_GUIDE.es.md               # Spanish Step-by-Step Instructor Demo Script
├── install.sh / install.ps1                  # Cross-platform environment & DB bootstrapper
├── requirements.txt / pyproject.toml         # Python dependencies & pytest configuration
├── data/
│   ├── seed_retail_data.py                   # Deterministic data generator (SQLite + CSV + JSONL)
│   ├── retail_pulse.db                       # Seeded SQLite database
│   ├── exports/                              # Commercial CSV exports (contracts, inventory, orders)
│   └── logs/                                 # POS/WMS webhooks & hook_compliance_audit.jsonl
├── src/
│   ├── main.py                               # FastAPI application & REST endpoints
│   ├── database.py / models.py               # SQLite connection & Pydantic schemas
│   ├── services/                             # promo_pricing, inventory_atp, vendor_otif, fulfillment_router
│   └── static/                               # index.html Command Center & tryolabs-logo.png
├── mcp_server/
│   └── retail_mcp.py                         # FastMCP server exposing 4 live retail tools
├── scripts/
│   ├── run_otif_margin_audit.py              # CLI audit helper for the Lab 02 Skill
│   └── margin_guard_hook.py                  # Deterministic PreToolUse compliance hook (Lab 03)
├── labs/
│   ├── lab-01-margin-inventory-triage/       # Starter, Solution, README (EN/ES), PROMPTS (EN/ES), scripts
│   ├── lab-02-rules-and-skills/              # Starter, Solution, README (EN/ES), PROMPTS (EN/ES), scripts
│   ├── lab-03-mcp-and-hooks/                 # Starter, Solution, README (EN/ES), PROMPTS (EN/ES), scripts
│   └── lab-04-multi-agent-capstone/          # Starter, Solution, README (EN/ES), PROMPTS (EN/ES), scripts
└── tests/
    ├── test_lab01_triage.py                  # 4 tests for Lab 01
    ├── test_lab02_rules_skills.py            # 3 tests for Lab 02
    ├── test_lab03_mcp_hooks.py               # 5 tests for Lab 03
    └── test_lab04_capstone.py                # 4 tests for Lab 04 (16 tests total)
```
