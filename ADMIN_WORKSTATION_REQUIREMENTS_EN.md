<div align="center">
  <img src="https://raw.githubusercontent.com/tryolabs/brand-assets/main/tryolabs-logo.png" alt="Tryolabs" height="44" />
</div>

# IT Administrator Workstation Requirements & Pre-Provisioning Guide — Retail Edition (Retail Pulse)
**Workshop**: Agentic Engineering with Google Antigravity — 4-Hour Hands-On Developer Workshop
**Edition**: Retail Edition (Retail Pulse) — Omnichannel Order Routing, True ATP Inventory Sync, Gross Margin Floor & Vendor OTIF Intelligence
**Repository**: `antigravity-workshop-retail`
**Delivered by**: Tryolabs

---

## 1. Executive Summary for IT Administrators (Zero-Privilege Attendee Mode)

Workshop attendees **do not have local administrator (`sudo` / Administrator) privileges** on their corporate computers and cannot install software, system binaries, or Python libraries during the live session.

To guarantee a seamless, zero-friction experience across all 4 hands-on labs in `antigravity-workshop-retail`, **IT Administrators must pre-install the requirements listed in this document prior to the workshop** and pre-populate the repository's `.venv` virtual environment. Once provisioned with the included `admin_provision_workstation.sh` (macOS/Linux) or `admin_provision_workstation.ps1` (Windows) script:
- **100% of Labs 1, 2, 3, and 4 execute in User Space** under standard, unprivileged user accounts.
- **Zero runtime package installations (`pip install` / `brew` / `apt` / `winget`)** are triggered during the workshop: all lab setup scripts (`./install.sh` and `./labs/lab-01-margin-inventory-triage/install.sh`) automatically detect the pre-provisioned `.venv` and run in **Zero-Install Mode**.
- **100% Local Database & Service Execution**: All data is stored in an embedded SQLite file (`data/retail_pulse.db`) inside `antigravity-workshop-retail/`—no external database servers or Docker daemons are required.

---

## 2. Hardware, Operating System, Local Ports & EDR/Firewall Rules

### 2.1 Hardware & OS Baseline
| Component | Minimum Requirement | Recommended Specification |
| :--- | :--- | :--- |
| **Operating System** | **macOS 13+** (Ventura/Sonoma/Sequoia), **Windows 10/11 (64-bit)** with Git Bash or WSL2, or **Linux** (Ubuntu 22.04+, Debian 12+, RHEL 9+) | macOS 14+ (Apple Silicon M1–M4) or Ubuntu 22.04+ / Windows 11 with WSL2 |
| **CPU & Memory (RAM)** | 4 vCPU cores / **8 GB RAM** | 8+ vCPU cores / **16 GB RAM** |
| **Free Disk Space** | **5 GB** free disk space in user workspace | **10 GB** free disk space |

### 2.2 Localhost TCP Loopback Ports (Unprivileged User Binding)
During the workshop, attendees launch the local FastAPI application and the Google ADK Development UI bound strictly to `127.0.0.1` (localhost). No inbound external network ports are opened:
- **TCP Port `8002` (`127.0.0.1:8002`)**: Retail Pulse Live Command Center Dashboard (`uvicorn src.main:app --port 8002`).
- **TCP Port `8080` (`127.0.0.1:8080`)**: Google ADK Development Web UI (`adk web adk_agents --port 8080` for `adk_agents/retail_pulse` via `./scripts/run_adk_web.sh`).

### 2.3 Endpoint Detection & Response (EDR / Antivirus) & Firewall Allowlist
1. **Local Subprocess Execution (`stdio`)**: In Lab 3, Google Antigravity spawns the local Python interpreter (`./.venv/bin/python`) as a child process over standard input/output (`stdio`) to run the FastMCP server (`mcp_server/retail_mcp.py`) and deterministic security hooks (`scripts/margin_guard_hook.py`). Ensure CrowdStrike Falcon, Microsoft Defender, or SentinelOne **do not block unprivileged Python subprocesses** inside `antigravity-workshop-retail/`.
2. **Outbound HTTPS Allowlist (Port `443`)**:
   - `*.googleapis.com` (`cloudaicompanion.googleapis.com`, `aiplatform.googleapis.com`, `discoveryengine.googleapis.com`, `run.googleapis.com`)
   - `accounts.google.com` and `oauth2.googleapis.com` (Google Cloud / Gemini Enterprise SSO authentication)

---

## 3. Complete System Software & CLI Binary Matrix

IT Administrators must install the following applications and command-line binaries system-wide and ensure they are accessible in the standard user's `PATH`:

| # | Software / Binary | Required Version | Verification Command | Used In `antigravity-workshop-retail` | Mandatory? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Google Antigravity** (Antigravity 2.0 Desktop App, Antigravity IDE, and `agy` CLI) | Latest Enterprise Release | `agy --version` (or launch Antigravity 2.0 / IDE) | All Labs (Labs 1–4) | **REQUIRED** |
| **2** | **Python 3 Runtime** (including `venv`, `pip`, `sqlite3`, `decimal` stdlib modules) | **>= 3.11** (`>= 3.10` compatible; **3.11 or 3.12 recommended**) | `python3 --version` | All Labs (Labs 1–4) | **REQUIRED** |
| **3** | **Astral `uv`** (Fast Python Package & Environment Manager) | **>= 0.5.0** | `uv --version` | `.venv` management & FastMCP execution | **REQUIRED** |
| **4** | **Git CLI** | **>= 2.39** | `git --version` | Cloning `antigravity-workshop-retail` & diff tracking | **REQUIRED** |
| **5** | **SQLite 3 CLI** | **>= 3.37** | `sqlite3 --version` | Inspecting `data/retail_pulse.db` & Lab 3 Hook testing | **REQUIRED** |
| **6** | **POSIX Shell (`bash`) & `curl`** | `bash >= 3.2` (macOS) / `>= 4.0` (Linux / Git Bash on Windows) | `bash --version` & `curl --version` | Running `./install.sh`, `./verify.sh`, and A2A checks | **REQUIRED** |
| **7** | **HashiCorp Terraform CLI** | **>= 1.5.0** | `terraform -version` | Lab 4 (`infra/terraform/` validation & Cloud Run deploy) | **REQUIRED for Lab 4** |
| **8** | **Google Cloud SDK (`gcloud`)** | **>= 460.0.0** | `gcloud --version` | Gemini Enterprise auth & Lab 4 GCP deployment | **REQUIRED for Lab 4** |
| **9** | **Chromium Web Browser** | Google Chrome or Microsoft Edge (Latest) | Launch browser | Viewing `:8002` dashboard, `:8080` `adk web`, & slides | **REQUIRED** |

### Platform Package Manager One-Liners for IT Admins
- **macOS (Homebrew)**:
  ```bash
  brew install python@3.12 uv git sqlite terraform
  brew install --cask google-cloud-sdk
  ```
- **Ubuntu / Debian Linux (`apt`)**:
  ```bash
  sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip git sqlite3 curl bash unzip
  curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/usr/local/bin" sh
  ```
- **Windows 10/11 (Elevated PowerShell via `winget`)**:
  ```powershell
  winget install -e --id Python.Python.3.12 --scope machine
  winget install -e --id Astral-sh.uv --scope machine
  winget install -e --id Git.Git --scope machine
  winget install -e --id SQLite.SQLite --scope machine
  winget install -e --id Hashicorp.Terraform --scope machine
  winget install -e --id Google.CloudSDK --scope machine
  ```

---

## 4. Complete Python Library Requirements (`requirements.txt` & `requirements-lock.txt`)

All Python packages must be pre-installed into `antigravity-workshop-retail/.venv` so attendees never run `pip install`.

### 4.1 Core Python Packages & Lab Mapping
| Package Name | Minimum Version | Verified Lock Version | Purpose in `antigravity-workshop-retail` Labs 1–4 |
| :--- | :--- | :--- | :--- |
| `fastapi` | `>=0.110.0` | `0.141.1` | Core REST API & A2A JSON-RPC 2.0 endpoint (`/api/v1/a2a`) across Labs 1–4 |
| `uvicorn` | `>=0.27.0` | `0.54.0` | Local ASGI web server hosting the live dashboard on `127.0.0.1:8002` |
| `pydantic` | `>=2.6.0` | `2.14.1` | Strict schema validation for GS1 GTIN-14 SKUs, WMS inventory nodes, promo rules, OTIF contracts, and A2A payloads |
| `pytest` | `>=8.0.0` | `9.1.1` | Automated verification runner for `verify.sh` across Labs 1, 2, 3, and 4 (20 passed) |
| `httpx` | `>=0.27.0` | `0.28.1` | FastAPI `TestClient` transport & async A2A client calls |
| `mcp` | `>=1.2.0` | `2.3.0` | Official Model Context Protocol SDK (`FastMCP`) for Lab 3 (`mcp_server/retail_mcp.py`) |
| `google-adk` | `>=1.0.0` | `2.12.0` | Google Agent Development Kit (`LlmAgent`, `Runner`, and `adk web` Dev UI for `adk_agents/retail_pulse`) |
| `google-genai` | `>=1.0.0` | `2.33.0` | Google GenAI / Vertex AI SDK used by ADK agents and Gemini Enterprise |
| `google-auth` | `>=2.28.0` | `2.62.0` | Google Cloud IAM & Application Default Credentials authentication |
| `aiosqlite` | `>=0.20.0` | `0.22.1` | Async SQLite session storage used by Google ADK (`adk web`) |
| `sse-starlette` | `>=2.0.0` | `3.5.0` | Server-Sent Events transport for FastMCP and ADK streaming |
| `starlette` | `>=0.36.0` | `1.9.0` | ASGI web routing and middleware |
| `websockets` | `>=12.0` | `15.0.1` | Real-time bidirectional streaming for `adk web` Dev UI (`:8080`) |
| `python-dotenv` | `>=1.0.0` | `1.2.4` | Environment variable loading for local vs. Vertex AI / Gemini Enterprise config |
| `python-multipart` | `>=0.0.9` | `0.0.32` | Form parsing required by FastAPI & ADK Web UI |
| `PyYAML` | `>=6.0.1` | `6.0.3` | YAML frontmatter parsing for Progressive Disclosure `SKILL.md` files (Lab 2) |
| `tenacity` | `>=8.2.0` | `9.1.4` | Retry resilience for agent tool execution |
| `requests` | `>=2.31.0` | `2.34.2` | HTTP client utilities |
| `opentelemetry-api` / `sdk` | `>=1.24.0` | `1.42.1` | Multi-agent trace telemetry surfaced in the `adk web` Development UI |

### 4.2 Offline / Air-Gapped Wheelhouse Support (Optional)
If attendee machines cannot reach `pypi.org` during provisioning, IT Admins can download all 59 pinned wheels once on a staging machine and bundle them into `antigravity-workshop-retail/wheelhouse/`:
```bash
pip download -r requirements-lock.txt -d ./wheelhouse
```
When `./wheelhouse` is present, both `./admin_provision_workstation.sh` and `./install.sh` automatically install 100% offline via `--no-index --find-links ./wheelhouse`.

---

## 5. Critical File Ownership & Permissions for Non-Admin Attendees

> **IMPORTANT FOR IT ADMINISTRATORS**:
> If you clone `antigravity-workshop-retail` and build `.venv` using an elevated `root` or `Administrator` account, **you MUST transfer recursive ownership of the entire `antigravity-workshop-retail` folder to the standard attendee user account** before the workshop starts.

Why is this required? During the hands-on labs, the unprivileged attendee runs scripts that create and modify files inside `antigravity-workshop-retail/`:
- `data/retail_pulse.db` (SQLite database + WAL journal files require write access to `data/`)
- `data/exports/` and `data/logs/hook_compliance_audit.jsonl` (Generated by Lab 2 Skills and Lab 3 Hooks)
- `GEMINI.md` and `.agents/` (`rules/`, `skills/`, `mcp_config.json`, `hooks.json` created in Labs 2 & 3)
- `src/services/`, `src/agents/`, and `mcp_server/retail_mcp.py` (Refactored during Labs 1, 3, and 4, and reset by `./labs/lab-01-margin-inventory-triage/install.sh`)

**Automated Fix (macOS / Linux)**:
```bash
sudo ./admin_requirements/admin_provision_workstation.sh --user <attendee_username>
```
**Manual Fix (macOS / Linux)**:
```bash
sudo chown -R <attendee_username>:<attendee_group> /path/to/antigravity-workshop-retail
sudo chmod -R u+rwX /path/to/antigravity-workshop-retail
```
**Manual Fix (Windows PowerShell as Admin)**:
```powershell
icacls "C:\Workshops\antigravity-workshop-retail" /grant "<AttendeeUser>:(OI)(CI)M" /T
```

---

## 6. Google Cloud APIs, IAM Roles & Permissions for Antigravity + Gemini Enterprise

To allow workshop attendees to authenticate **Google Antigravity** (`agy`, Antigravity IDE, and Antigravity 2.0) with **Gemini Enterprise**, execute **Google ADK (`adk web`)** against **Vertex AI**, and deploy/register the **`retail-pulse`** A2A agent in Lab 4, the Cloud Administrator must enable the following APIs and grant the following IAM roles on the workshop Google Cloud project (`<WORKSHOP_GCP_PROJECT_ID>`).

### 6.1 Required Google Cloud APIs to Enable (`gcloud services enable`)
| Google Cloud API Service Name | Service Title | Purpose in `antigravity-workshop-retail` | Status |
| :--- | :--- | :--- | :--- |
| `cloudaicompanion.googleapis.com` | **Gemini for Google Cloud API** (Cloud AI Companion API) | Core backend API for **Google Antigravity** (`agy`, IDE, 2.0) under Gemini Enterprise subscriptions, code generation, agentic tool use, and license seat verification | **REQUIRED (All Labs)** |
| `aiplatform.googleapis.com` | **Vertex AI API** | Powers **Google Agent Development Kit (`google-adk`)** and `google-genai` SDK (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`) for Lab 4 multi-agent execution and `adk web` | **REQUIRED (Lab 4)** |
| `discoveryengine.googleapis.com` | **Gemini Enterprise / Discovery Engine API** | Registers and invokes the `retail-pulse` A2A (`AgentCard`) endpoint inside Gemini Enterprise (`./deploy/register_gemini_enterprise_agent.sh`) | **REQUIRED (Lab 4)** |
| `serviceusage.googleapis.com` | **Service Usage API** | Allows attendees to validate enabled APIs and bind quota calls to the workshop project (`x-goog-user-project`) | **REQUIRED (All Labs)** |
| `cloudresourcemanager.googleapis.com` | **Cloud Resource Manager API** | Project metadata inspection and Terraform provider initialization | **REQUIRED (Lab 4)** |
| `run.googleapis.com` | **Cloud Run Admin API** | Deploys the containerized `retail-pulse` FastAPI + ADK + A2A service to Cloud Run v2 (`infra/terraform/`) | **REQUIRED (Lab 4 Deploy)** |
| `artifactregistry.googleapis.com` | **Artifact Registry API** | Stores the `retail-pulse` Docker container image (`retail-pulse-repo`) | **REQUIRED (Lab 4 Deploy)** |
| `cloudbuild.googleapis.com` | **Cloud Build API** | Builds the `retail-pulse` container image via `gcloud builds submit` | **REQUIRED (Lab 4 Deploy)** |
| `iam.googleapis.com` | **Identity and Access Management (IAM) API** | Provisions the least-privilege Cloud Run service account (`retail-pulse-sa`) | **REQUIRED (Lab 4 Deploy)** |
| `logging.googleapis.com` | **Cloud Logging API** | Records `cloudaicompanion.googleapis.com` Cloud Audit Logs and Cloud Run container telemetry | **REQUIRED (All Labs)** |

### 6.2 Required IAM Roles & Underlying Permissions for Workshop Attendees (`user:<attendee>@company.com`)
In addition to assigning an active **Gemini Enterprise / Gemini Code Assist Enterprise license seat** to each attendee in the Google Cloud Console (**Admin for Gemini -> License Management**), grant each attendee the following IAM roles on the workshop GCP project:

| IAM Role ID | Role Title | Key Included IAM Permissions | Why It Is Required |
| :--- | :--- | :--- | :--- |
| `roles/cloudaicompanion.user` | **Gemini for Google Cloud User** | `cloudaicompanion.companions.generateChat`, `cloudaicompanion.companions.generateCode`, `cloudaicompanion.instances.completeCode`, `cloudaicompanion.instances.generateChat`, `cloudaicompanion.instances.generateCode`, `cloudaicompanion.instances.queryEffectiveSetting`, `cloudaicompanion.entitlements.get` | **Mandatory for Google Antigravity**: Authorizes the developer to authenticate `agy`, Antigravity IDE, and Antigravity 2.0 with Gemini Enterprise and invoke agentic completions |
| `roles/serviceusage.serviceUsageConsumer` | **Service Usage Consumer** | `serviceusage.services.use`, `serviceusage.services.get`, `serviceusage.services.list` | **Mandatory for Quota Billing**: Allows the attendee's CLI/IDE session (`gcloud auth application-default set-quota-project`) to use the workshop GCP project's API quota |
| `roles/aiplatform.user` | **Vertex AI User** | `aiplatform.endpoints.predict`, `aiplatform.endpoints.generateContent`, `aiplatform.endpoints.streamGenerateContent`, `aiplatform.models.get` | **Mandatory for Lab 4 ADK**: Allows `adk web adk_agents` (`adk_agents/retail_pulse`) and the ADK `Runner` to invoke Gemini models on Vertex AI (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`) |
| `roles/discoveryengine.editor` *(or `roles/discoveryengine.viewer`)* | **Discovery Engine Editor / Viewer** | `discoveryengine.engines.get`, `discoveryengine.engines.list`, `discoveryengine.assistants.get`, `discoveryengine.agents.create`, `discoveryengine.agents.update` | **Required for Lab 4 Gemini Enterprise**: Allows inspecting Gemini Enterprise engines and registering the `retail-pulse` A2A agent card (`/.well-known/agent.json`) |
| `roles/viewer` | **Project Viewer** | `resourcemanager.projects.get`, `run.services.get`, `run.services.list` | **Recommended**: Allows attendees to view the deployed `retail-pulse` Cloud Run URL and project configuration |

### 6.3 Additional IAM Roles for Cloud Admin / Instructor & Cloud Run Runtime Service Account
| Principal / Persona | Required IAM Roles | Purpose |
| :--- | :--- | :--- |
| **Cloud Admin / Workshop Instructor** (`user:<instructor>@company.com`) | `roles/cloudaicompanion.admin`, `roles/logging.privateLogViewer`, `roles/run.admin`, `roles/artifactregistry.admin`, `roles/cloudbuild.builds.editor`, `roles/iam.serviceAccountAdmin`, `roles/iam.serviceAccountUser`, `roles/serviceusage.serviceUsageAdmin` | Assigns Gemini Enterprise seats, demonstrates `cloudaicompanion.googleapis.com` Cloud Audit Logs in Block 1, and runs `terraform apply` (`infra/terraform/`) to deploy `retail-pulse` to Cloud Run v2 |
| **Cloud Run Runtime Service Account** (`retail-pulse-sa@<project>.iam.gserviceaccount.com`) | `roles/aiplatform.user`, `roles/discoveryengine.viewer`, `roles/logging.logWriter` | Automatically provisioned by `infra/terraform/main.tf` as the least-privilege identity attached to the `retail-pulse` Cloud Run v2 service |

### 6.4 One-Step `gcloud` Provisioning Commands for Cloud Administrators
```bash
export PROJECT_ID="<WORKSHOP_GCP_PROJECT_ID>"

# 1. Enable all required Google Cloud APIs for Antigravity, Gemini Enterprise, Vertex AI, ADK & Cloud Run
gcloud services enable \
  cloudaicompanion.googleapis.com \
  aiplatform.googleapis.com \
  discoveryengine.googleapis.com \
  serviceusage.googleapis.com \
  cloudresourcemanager.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com \
  logging.googleapis.com \
  --project="${PROJECT_ID}"

# 2. Grant required IAM roles to each Workshop Attendee
export ATTENDEE_EMAIL="<attendee>@company.com"
for ROLE in \
  roles/cloudaicompanion.user \
  roles/serviceusage.serviceUsageConsumer \
  roles/aiplatform.user \
  roles/discoveryengine.editor \
  roles/viewer; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="user:${ATTENDEE_EMAIL}" \
    --role="${ROLE}"
done
```

---

## 7. Pre-Workshop Verification Checklist for IT Admins

Run `./admin_requirements/admin_provision_workstation.sh --verify-only` as the **standard (non-admin) attendee user** and confirm all checks pass:

1. `python3 --version` returns `Python 3.10+` (`3.11` or `3.12` recommended).
2. `uv --version` returns `uv 0.5+`.
3. `git --version` and `sqlite3 --version` return valid versions from `PATH`.
4. `terraform -version` and `gcloud --version` are available in `PATH` (for Lab 4).
5. Google Antigravity (`Antigravity 2.0`, `Antigravity IDE`, and/or `agy` CLI) opens and authenticates cleanly with `roles/cloudaicompanion.user` and `roles/serviceusage.serviceUsageConsumer`.
6. `./.venv/bin/python -c "import fastapi, uvicorn, pydantic, pytest, httpx, mcp, google.adk, google.genai"` exits with code `0`.
7. `./.venv/bin/adk --version` and `./scripts/run_adk_web.sh --check` succeed with code `0`.
8. Running `./install.sh` prints `[OK] Pre-provisioned .venv detected with all required packages (zero-install mode)` and seeds `data/retail_pulse.db` without errors.
9. Running `./verify.sh` (with all solutions applied) passes 100% of automated tests (`20 passed`).
10. Localhost TCP ports `8002` and `8080` can be bound by the standard user without firewall prompts.
