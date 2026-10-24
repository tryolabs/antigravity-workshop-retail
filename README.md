<div align="center">
  <img src="src/static/tryolabs-logo.png" alt="Tryolabs Logo" height="48" />
  <h1>Retail Pulse — Google Antigravity Hands-On Workshop</h1>
  <p><strong>Omnichannel Order, Inventory Sync & Commercial Margin / Vendor Contract Intelligence Platform</strong></p>
  <p><em>Delivered by <strong>Tryolabs</strong> | 4-Hour Enterprise Retail & Omnichannel Commerce Workshop</em></p>
  <p><a href="README.md"><strong>English</strong></a> | <a href="README.es.md"><strong>Español</strong></a></p>
</div>

---

## 1. Executive Summary & Dual-Track Design

Welcome to the **Google Antigravity Retail Industry Workshop**, designed and delivered by **Tryolabs**.

During peak seasonal events (Flash Sales / Black Friday), retail enterprises face an intersecting crisis across **Platform Engineering** and **Commercial / Merchandising Operations**:
1. **Unclamped Promotional Discount Stacking (`-$35,113.25` Margin Bleed)**: Campaign promo codes stack multiplicatively with loyalty tier discounts without enforcing the 15% gross margin floor (`minimum_margin_pct`), selling flagship items below wholesale unit cost.
2. **Phantom Inventory & Stockout Risk (`$250,000+` VIP LTV Exposed)**: The Available-to-Promise (`ATP`) engine checks raw `on_hand_qty` while ignoring `reserved_bopis_qty`, `damaged_hold_qty`, and `safety_stock_qty`, stranding **35 VIP (`DIAMOND`/`GOLD`) orders** in `AT_RISK_STOCKOUT`.
3. **Unclaimed Vendor OTIF Penalties (`$98,250.00` Recoverable Chargebacks)**: 6 of 10 strategic suppliers are breaching contractual On-Time In-Full (`OTIF`) SLAs (`actual_otif_pct < contracted_otif_pct`), leaving nearly `$100K` in contractual chargebacks unclaimed.

This repository supports **both Technical Engineers and Commercial/Operations Managers** working side by side:
- **Technical Track (Software, Data & Platform Engineers)**: Debug Python/FastAPI microservices, write `pytest` suites, build FastMCP tools (`mcp_server/retail_mcp.py`), enforce deterministic `PreToolUse` hooks (`scripts/margin_guard_hook.py`), orchestrate multi-agent systems with **Google ADK (Agent Development Kit)** and **A2A (Agent2Agent Protocol)** (`src/agents/adk_a2a_orchestrator.py`), test interactively with **`adk web`** (`scripts/run_adk_web.sh`), and deploy to **Google Cloud Run + Gemini Enterprise** via **Terraform** (`infra/terraform/`).
- **Commercial Track (Merchandising, Category Management & Supply Chain Operations)**: Audit CSV exports (`data/exports/`), encode corporate margin & OTIF rules (`GEMINI.md`, `.agents/rules/retail-standards.md`), create reusable executive audit skills (`.agents/skills/`), query live retail databases through natural-language MCP tools, and validate KPIs in the live **Retail Pulse Command Center** (`http://127.0.0.1:8002`) and **ADK Web UI** (`http://127.0.0.1:8080`).

---

## 2. System Architecture (Antigravity + FastMCP + Google ADK + A2A + Cloud Run)

```text
+---------------------------------------------------------------------------------------------------+
|                           GOOGLE ANTIGRAVITY IDE & AGENT RUNTIME                                  |
|  - Slash Commands: /plan, /boost, /teamwork, /browser, /learn, /compact, /goal                    |
|  - Customizations: GEMINI.md | .agents/rules/ | .agents/skills/ | .agents/hooks.json              |
+------------------+-----------------------------------+-----------------------------------+--------+
                   |                                   |                                   |
     Stdio FastMCP |                      HTTP / REST  |                 A2A JSON-RPC 2.0  |
                   v                                   v                                   v
+------------------+-------------------+ +-------------+--------------------+ +------------+--------+
| MCP SERVER (mcp_server/retail_mcp.py)| | FASTAPI COMMAND CENTER (main.py) | | GOOGLE ADK & A2A    |
| - query_true_atp_inventory           | | - Web UI: src/static/index.html  | | - /.well-known/     |
| - audit_vendor_otif_contracts        | | - promo_pricing.py (Lab 01)      | |   agent.json        |
| - simulate_promo_margin_guard        | | - inventory_atp.py (Lab 01)      | | - POST /api/v1/a2a  |
| - list_at_risk_vip_orders            | | - fulfillment_router.py (Lab 04) | | - adk web (:8080)   |
+------------------+-------------------+ +-------------+--------------------+ +------------+--------+
                   |                                   |                                   |
                   +-----------------------------------+-----------------------------------+
                                                       |
                                                       v
+---------------------------------------------------------------------------------------------------+
|                DETERMINISTIC RETAIL DATA LAYER (data/) & CLOUD DEPLOYMENT (infra/ + deploy/)      |
|  - SQLite DB: data/retail_pulse.db | CSV Exports: data/exports/ | Logs: data/logs/                |
|  - Terraform IaC: infra/terraform/ (Cloud Run v2 + Artifact Registry + Vertex AI + IAM)           |
|  - Gemini Enterprise Registration: deploy/register_gemini_enterprise_agent.sh                     |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. 4-Hour Workshop Curriculum & Lab Matrix

| Module | Duration | Focus Area & Antigravity Capabilities | Lab Guide & Prompt Playbook | Automation Scripts |
| :--- | :--- | :--- | :--- | :--- |
| **Setup & Briefing** | `00:00 - 00:30` | Environment setup, Retail Pulse Command Center tour, Antigravity IDE + Agent Manager overview | [Quickstart Guide](#4-quickstart-instructions) | `./install.sh` (or `./install.ps1`) |
| **Lab 01** | `00:30 - 01:15` | **Omnichannel Flash-Sale Triage**: Context `@` mentions, `/plan`, Inline Edit (`Cmd+I`), fixing Promo Margin Stacking (Bug #1A) & Phantom ATP Inventory (Bug #1B) | [Lab 01 Guide (EN)](labs/lab-01-margin-inventory-triage/README.md) \| [ES](labs/lab-01-margin-inventory-triage/README.es.md)<br>[Prompts (EN)](labs/lab-01-margin-inventory-triage/PROMPTS.md) \| [ES](labs/lab-01-margin-inventory-triage/PROMPTS.es.md) | `labs/lab-01-margin-inventory-triage/{install.sh,verify.sh,apply_solution.sh,deploy_gcp.sh}` |
| **Lab 02** | `01:15 - 02:00` | **Customizations (`GEMINI.md`, Rules & Skills)**: Encoding GS1 GTIN-14, 15% margin floor & OTIF standards in `.agents/rules/retail-standards.md` and building `.agents/skills/margin-otif-audit/SKILL.md` | [Lab 02 Guide (EN)](labs/lab-02-rules-and-skills/README.md) \| [ES](labs/lab-02-rules-and-skills/README.es.md)<br>[Prompts (EN)](labs/lab-02-rules-and-skills/PROMPTS.md) \| [ES](labs/lab-02-rules-and-skills/PROMPTS.es.md) | `labs/lab-02-rules-and-skills/{install.sh,verify.sh,apply_solution.sh,deploy_gcp.sh}` |
| **Lab 03** | `02:00 - 02:55` | **FastMCP Server, Deterministic Hooks & Enterprise Governance**: Building `mcp_server/retail_mcp.py`, `.agents/mcp_config.json`, `PreToolUse` hook (`scripts/margin_guard_hook.py`), and Gemini Enterprise / Cloud Security | [Lab 03 Guide (EN)](labs/lab-03-mcp-and-hooks/README.md) \| [ES](labs/lab-03-mcp-and-hooks/README.es.md)<br>[Prompts (EN)](labs/lab-03-mcp-and-hooks/PROMPTS.md) \| [ES](labs/lab-03-mcp-and-hooks/PROMPTS.es.md) | `labs/lab-03-mcp-and-hooks/{install.sh,verify.sh,apply_solution.sh,deploy_gcp.sh}` |
| **Lab 04** | `02:55 - 03:45` | **Multi-Agent Capstone (Google ADK, A2A, `adk web`, Cloud Run & Gemini Enterprise)**: Building Smart Split-Shipment Routing (`fulfillment_router.py`), ADK + A2A Orchestrator (`adk_a2a_orchestrator.py`), testing via `adk web`, and deploying via Terraform to Cloud Run & Gemini Enterprise | [Lab 04 Guide (EN)](labs/lab-04-multi-agent-capstone/README.md) \| [ES](labs/lab-04-multi-agent-capstone/README.es.md)<br>[Prompts (EN)](labs/lab-04-multi-agent-capstone/PROMPTS.md) \| [ES](labs/lab-04-multi-agent-capstone/PROMPTS.es.md) | `labs/lab-04-multi-agent-capstone/{install.sh,verify.sh,apply_solution.sh,deploy_gcp.sh}` |
| **Wrap-Up** | `03:45 - 04:00` | Production rollout patterns, Q&A with Tryolabs solutions architects | [Lab 04 Guide (EN)](labs/lab-04-multi-agent-capstone/README.md) | `./labs/lab-04-multi-agent-capstone/verify.sh` |

---

## 4. Quickstart Instructions

### Prerequisites
- **Python 3.10+**
- **Google Antigravity** (Desktop IDE or `agy` CLI)
- macOS, Linux, or Windows (PowerShell)

### 1. Bootstrap the Workshop Environment
Run the root installer to create the `.venv` virtual environment, install dependencies (`fastapi`, `uvicorn`, `pydantic`, `pytest`, `httpx`, `mcp`, `google-adk`), seed the deterministic retail database (`data/retail_pulse.db`), generate CSV exports (`data/exports/`), and initialize **Lab 01 Starter State**:

**macOS / Linux:**
```bash
./install.sh
```

**Windows (PowerShell):**
```powershell
.\install.ps1
```

### 2. Launch the Live Retail Pulse Command Center
Start the FastAPI server and open `http://127.0.0.1:8002` in your browser:

```bash
.venv/bin/uvicorn src.main:app --reload --port 8002
```

You will see the **Retail Pulse Command Center** (branded with **Delivered by Tryolabs**) displaying the initial crisis metrics:
- **Margin Hold Orders**: `30` orders (`-$35,113.25` Margin Bleed)
- **VIP Stockout Risk**: `35` VIP orders (`$250,000+` Customer LTV exposed)
- **OTIF Chargeback Recovery**: `6` breaching vendors (`$98,250.00` recoverable penalties)

### 3. Test Multi-Agent Orchestration Locally with `adk web` (Lab 04)
Launch the interactive **Google ADK Development UI** to inspect the `retail_pulse_root_agent` and its sub-agents (`wms_inventory_agent`, `merchandising_margin_agent`, and `a2a_bridge_agent`):

```bash
# Dry-run validation:
./scripts/run_adk_web.sh --dry-run

# Launch interactive ADK Web UI at http://127.0.0.1:8080:
./scripts/run_adk_web.sh --port 8080
```

### 4. Deploy to Google Cloud Run via Terraform & Register in Gemini Enterprise
Validate or execute the full Cloud Run + Terraform + Gemini Enterprise A2A registration pipeline:

```bash
# Dry-run validation (no GCP credentials required):
./deploy/deploy_gcp.sh --dry-run --project-id my-retail-gcp-project --region us-central1 --gemini-app-id retail-pulse-enterprise-app

# Live GCP deployment & Gemini Enterprise registration:
./deploy/deploy_gcp.sh --project-id YOUR_GCP_PROJECT_ID --region us-central1 --gemini-app-id YOUR_GEMINI_ENTERPRISE_APP_ID
```

### 5. Run Lab Installers, Verifiers & Solution Scripts
Every lab folder (`labs/lab-01-*` through `labs/lab-04-*`) is completely self-contained and includes:
- `./labs/<lab-name>/install.sh` — Resets the workspace to the exact starter state for that lab (automatically applying prerequisites from earlier labs).
- `./labs/<lab-name>/verify.sh` — Runs the automated `pytest` verification suite for that lab.
- `./labs/<lab-name>/apply_solution.sh` — Instantly applies the reference solution for that lab.
- `./labs/<lab-name>/deploy_gcp.sh` — Deploys the current lab's microservice & A2A agent to Google Cloud Run via Terraform.

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
- **Command Allowlist / Denylist & Browser Allowlist**: Allowlist safe test runners (`.venv/bin/python -m pytest`) while blocking destructive shell commands (`rm -rf`, `curl`) and restricting `/browser` to `http://127.0.0.1:8002`.
- **Deterministic Lifecycle Hooks (`.agents/hooks.json`)**: Execute deterministic pre-tool validation (`scripts/margin_guard_hook.py`) before any file modification occurs, blocking 15% margin floor bypasses with `"decision": "deny"` and recording every decision to `data/logs/hook_compliance_audit.jsonl`.

---

## 6. Repository Structure

```text
antigravity-workshop-retail/
├── README.md / README.es.md                  # Bilingual Workshop Guides (EN/ES)
├── install.sh / install.ps1                  # Cross-platform environment & DB bootstrapper
├── Dockerfile / .dockerignore                # Production Cloud Run container definition
├── requirements.txt / pyproject.toml         # Python dependencies (including google-adk & mcp)
├── adk_agents/
│   └── retail_pulse/                         # Google ADK package for local `adk web` testing
│       ├── __init__.py
│       └── agent.py                          # Defines `root_agent` + WMS & Merchandising sub-agents
├── infra/
│   └── terraform/                            # Terraform IaC for Cloud Run, Artifact Registry & IAM
│       ├── main.tf / variables.tf / outputs.tf / versions.tf
│       └── terraform.tfvars.example
├── deploy/
│   ├── deploy_gcp.sh / deploy_gcp.ps1        # Cloud Build + Terraform Cloud Run deployment script
│   └── register_gemini_enterprise_agent.sh   # Registers Cloud Run A2A Agent in Gemini Enterprise
├── data/
│   ├── seed_retail_data.py                   # Deterministic data generator (SQLite + CSV + JSONL)
│   ├── retail_pulse.db                       # Seeded SQLite database
│   ├── exports/                              # Commercial CSV exports (contracts, inventory, orders)
│   └── logs/                                 # POS/WMS webhooks & hook_compliance_audit.jsonl
├── src/
│   ├── main.py                               # FastAPI app, REST endpoints & A2A Protocol endpoints
│   ├── database.py / models.py               # SQLite connection & Pydantic schemas
│   ├── agents/
│   │   └── adk_a2a_orchestrator.py           # Google ADK & A2A Multi-Agent Orchestrator (Lab 04)
│   ├── services/                             # promo_pricing, inventory_atp, fulfillment_router
│   └── static/                               # index.html Command Center & tryolabs-logo.png
├── mcp_server/
│   └── retail_mcp.py                         # FastMCP server exposing 4 live retail tools
├── scripts/
│   ├── run_otif_margin_audit.py              # CLI audit helper for the Lab 02 Skill
│   ├── margin_guard_hook.py                  # Deterministic PreToolUse compliance hook (Lab 03)
│   └── run_adk_web.sh                        # Launches `adk web` local multi-agent UI (Lab 04)
├── labs/
│   ├── lab-01-margin-inventory-triage/       # Starter, Solution, README (EN/ES), PROMPTS (EN/ES), scripts
│   ├── lab-02-rules-and-skills/              # Starter, Solution, README (EN/ES), PROMPTS (EN/ES), scripts
│   ├── lab-03-mcp-and-hooks/                 # Starter, Solution, README (EN/ES), PROMPTS (EN/ES), scripts
│   └── lab-04-multi-agent-capstone/          # Starter, Solution, README (EN/ES), PROMPTS (EN/ES), scripts
└── tests/
    ├── test_lab01_triage.py                  # 6 tests for Lab 01
    ├── test_lab02_rules_skills.py            # 4 tests for Lab 02
    ├── test_lab03_mcp_hooks.py               # 3 tests for Lab 03
    └── test_lab04_capstone.py                # 7 tests for Lab 04 (20 tests total)
```
