<div align="center">
  <img src="https://raw.githubusercontent.com/tryolabs/brand-assets/main/tryolabs-logo.png" alt="Tryolabs" height="44" />
</div>

# IT Administrator Workstation Requirements & Pre-Provisioning Guide
**Workshop**: Agentic Engineering with Google Antigravity — 4-Hour Hands-On Developer Workshop (Telecom & Retail Editions)
**Delivered by**: Tryolabs
**Target Audience**: Corporate IT Administrators, Endpoint Security Engineers, and Workstation Provisioning Teams

---

## 1. Executive Summary for IT Administrators (Zero-Privilege Attendee Mode)

Workshop attendees **do not have local administrator (`sudo` / Administrator) privileges** on their corporate computers and cannot install software, system binaries, or Python packages during the live session.

To guarantee a seamless, zero-friction experience across all 4 hands-on labs, **IT Administrators must pre-install the requirements listed in this document prior to the workshop** and pre-populate the repository's `.venv` virtual environment. Once provisioned with the included `admin_provision_workstation.sh` (macOS/Linux) or `admin_provision_workstation.ps1` (Windows) script:
- **100% of Labs 1, 2, 3, and 4 execute in User Space** with standard, unprivileged user accounts.
- **Zero runtime package installations (`pip install` / `brew` / `apt` / `winget`)** are triggered during the workshop: all lab setup scripts (`./install.sh` and `./labs/lab-0X-.../install.sh`) automatically detect the pre-provisioned `.venv` and run in **Zero-Install Mode**.
- **100% Local Database & Service Execution**: All data is stored in an embedded SQLite file (`data/telecom_nexus.db` or `data/retail_pulse.db`) inside the repository directory—no external database servers or Docker daemons are required.

---

## 2. Hardware, Operating System, Local Ports & EDR/Firewall Rules

### 2.1 Hardware & OS Baseline
| Component | Minimum Requirement | Recommended Specification |
| :--- | :--- | :--- |
| **Operating System** | **macOS 13+** (Ventura/Sonoma/Sequoia), **Windows 10/11 (64-bit)** with Git Bash or WSL2, or **Linux** (Ubuntu 22.04+, Debian 12+, RHEL 9+) | macOS 14+ (Apple Silicon M1–M4) or Ubuntu 22.04+ / Windows 11 with WSL2 |
| **CPU & Memory (RAM)** | 4 vCPU cores / **8 GB RAM** | 8+ vCPU cores / **16 GB RAM** |
| **Free Disk Space** | **5 GB** free disk space in user workspace | **10 GB** free disk space |

### 2.2 Localhost TCP Loopback Ports (Unprivileged User Binding)
During the workshop, attendees launch local Python FastAPI servers and the Google ADK Development UI bound strictly to `127.0.0.1` (localhost). No inbound external network ports are opened:
- **TCP Port `8001` (`127.0.0.1:8001`)**: Telecom Nexus Live Web NOC Dashboard (`uvicorn src.main:app --port 8001`).
- **TCP Port `8002` (`127.0.0.1:8002`)**: Retail Pulse Live Command Center UI (`uvicorn src.main:app --port 8002`).
- **TCP Port `8080` (`127.0.0.1:8080`)**: Google ADK Development Web UI (`adk web --port 8080` via `./scripts/run_adk_web.sh`).

### 2.3 Endpoint Detection & Response (EDR / Antivirus) & Firewall Allowlist
1. **Local Subprocess Execution (`stdio`)**: In Lab 3, Google Antigravity spawns the local Python interpreter (`./.venv/bin/python`) as a child process over standard input/output (`stdio`) to run the FastMCP server (`mcp_server/telecom_mcp.py` or `mcp_server/retail_mcp.py`) and deterministic security hooks (`scripts/audit_hook.py`). Ensure CrowdStrike Falcon, Microsoft Defender, or SentinelOne **do not block unprivileged Python subprocesses** inside the workshop repository directory.
2. **Outbound HTTPS Allowlist (Port `443`)**:
   - `*.googleapis.com` (`cloudaicompanion.googleapis.com`, `aiplatform.googleapis.com`, `discoveryengine.googleapis.com`, `run.googleapis.com`)
   - `accounts.google.com` and `oauth2.googleapis.com` (Google Cloud / Gemini Enterprise SSO authentication)

---

## 3. Complete System Software & CLI Binary Matrix

IT Administrators must install the following applications and command-line binaries system-wide and ensure they are accessible in the standard user's `PATH`:

| # | Software / Binary | Required Version | Verification Command | Used In | Mandatory? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Google Antigravity** (Antigravity 2.0 Desktop App, Antigravity IDE, and `agy` CLI) | Latest Enterprise Release | `agy --version` (or launch Antigravity 2.0 / IDE) | All Labs (Labs 1–4) | **REQUIRED** |
| **2** | **Python 3 Runtime** (including `venv`, `pip`, `sqlite3`, `decimal` stdlib modules) | **>= 3.11** (`>= 3.10` compatible; **3.11 or 3.12 recommended**) | `python3 --version` | All Labs (Labs 1–4) | **REQUIRED** |
| **3** | **Astral `uv`** (Fast Python Package & Environment Manager) | **>= 0.5.0** | `uv --version` | Environment management & MCP execution | **REQUIRED** |
| **4** | **Git CLI** | **>= 2.39** | `git --version` | Cloning & workspace diff tracking | **REQUIRED** |
| **5** | **SQLite 3 CLI** | **>= 3.37** | `sqlite3 --version` | Lab 1 & Lab 3 database inspection & hook testing | **REQUIRED** |
| **6** | **POSIX Shell (`bash`) & `curl`** | `bash >= 3.2` (macOS) / `>= 4.0` (Linux / Git Bash on Windows) | `bash --version` & `curl --version` | Running `./install.sh`, `./verify.sh`, and A2A tests | **REQUIRED** |
| **7** | **HashiCorp Terraform CLI** | **>= 1.5.0** | `terraform -version` | Lab 4 (`infra/terraform/` validation & Cloud Run deploy) | **REQUIRED for Lab 4** |
| **8** | **Google Cloud SDK (`gcloud`)** | **>= 460.0.0** | `gcloud --version` | Gemini Enterprise auth & Lab 4 GCP deployment | **REQUIRED for Lab 4** |
| **9** | **Chromium Web Browser** | Google Chrome or Microsoft Edge (Latest) | Launch browser | Viewing `:8001`/`:8002` UI, `:8080` `adk web`, & HTML slides | **REQUIRED** |

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

All Python packages must be pre-installed into the repository's `.venv` virtual environment (`antigravity-workshop-telecom/.venv` and/or `antigravity-workshop-retail/.venv`) so attendees never run `pip install`.

### 4.1 Core Python Packages & Lab Mapping
| Package Name | Minimum Version | Verified Lock Version | Purpose in Workshop Labs |
| :--- | :--- | :--- | :--- |
| `fastapi` | `>=0.110.0` | `0.141.1` | Core REST API & A2A JSON-RPC 2.0 endpoint (`/api/v1/a2a`) across Labs 1–4 |
| `uvicorn` | `>=0.27.0` | `0.54.0` | Local ASGI web server hosting the live Telecom/Retail dashboards (`:8001`/`:8002`) |
| `pydantic` | `>=2.6.0` | `2.14.1` | Strict schema validation for CDRs, 5G slices, WMS inventory, and A2A payloads |
| `pytest` | `>=8.0.0` | `9.1.1` | Automated verification runner for `verify.sh` across Labs 1, 2, 3, and 4 |
| `httpx` | `>=0.27.0` | `0.28.1` | FastAPI `TestClient` transport & async A2A client calls |
| `mcp` | `>=1.2.0` | `2.3.0` | Official Model Context Protocol SDK (`FastMCP`) for Lab 3 local `stdio` MCP server |
| `google-adk` | `>=1.0.0` | `2.12.0` | Google Agent Development Kit (`LlmAgent`, `Runner`, and `adk web` Dev UI in Lab 4) |
| `google-genai` | `>=1.0.0` | `2.33.0` | Google GenAI / Vertex AI SDK used by ADK agents and Gemini Enterprise |
| `google-auth` | `>=2.28.0` | `2.62.0` | Google Cloud IAM & Application Default Credentials authentication |
| `aiosqlite` | `>=0.20.0` | `0.22.1` | Async SQLite session storage used by Google ADK (`adk web`) |
| `sse-starlette` | `>=2.0.0` | `3.5.0` | Server-Sent Events transport for FastMCP and ADK streaming |
| `starlette` | `>=0.36.0` | `1.9.0` | ASGI web routing and middleware |
| `websockets` | `>=12.0` | `15.0.1` | Real-time bidirectional streaming for `adk web` Dev UI |
| `python-dotenv` | `>=1.0.0` | `1.2.4` | Environment variable loading for local vs. Vertex AI / Gemini Enterprise config |
| `python-multipart` | `>=0.0.9` | `0.0.32` | Form parsing required by FastAPI & ADK Web UI |
| `PyYAML` | `>=6.0.1` | `6.0.3` | YAML frontmatter parsing for Progressive Disclosure `SKILL.md` files (Lab 2) |
| `tenacity` | `>=8.2.0` | `9.1.4` | Retry resilience for agent tool execution |
| `requests` | `>=2.31.0` | `2.34.2` | HTTP client utilities |
| `opentelemetry-api` / `sdk` | `>=1.24.0` | `1.42.1` | Agent trace telemetry surfaced in the `adk web` Development UI |

### 4.2 Offline / Air-Gapped Wheelhouse Support (Optional)
If attendee machines cannot reach `pypi.org` during provisioning, IT Admins can download all 59 pinned wheels once on a staging machine and bundle them into a `./wheelhouse` directory inside the repository:
```bash
pip download -r requirements-lock.txt -d ./wheelhouse
```
When `./wheelhouse` is present, both `./admin_provision_workstation.sh` and `./install.sh` automatically install 100% offline via `--no-index --find-links ./wheelhouse`.

---

## 5. Critical File Ownership & Permissions for Non-Admin Attendees

> **IMPORTANT FOR IT ADMINISTRATORS**:
> If you clone the repository and build `.venv` using an elevated `root` or `Administrator` account, **you MUST transfer recursive ownership of the entire repository folder to the standard attendee user account** before the workshop starts.

Why is this required? During the hands-on labs, the unprivileged attendee runs scripts that create and modify files inside the repository:
- `data/telecom_nexus.db` or `data/retail_pulse.db` (SQLite database + WAL journal files require write access to `data/`)
- `data/exports/` and `data/logs/hook_audit.log` (Generated by Lab 2 Skills and Lab 3 Hooks)
- `GEMINI.md` and `.agents/` (`rules/`, `skills/`, `mcp_config.json`, `hooks.json` created in Labs 2 & 3)
- `src/services/`, `src/agents/`, and `mcp_server/` (Refactored during Labs 1, 3, and 4, and reset by `./labs/lab-0X-.../install.sh`)

**Automated Fix (macOS / Linux)**:
```bash
sudo ./admin_requirements/admin_provision_workstation.sh --user <attendee_username>
```
**Manual Fix (macOS / Linux)**:
```bash
sudo chown -R <attendee_username>:<attendee_group> /path/to/antigravity-workshop-telecom
sudo chmod -R u+rwX /path/to/antigravity-workshop-telecom
```
**Manual Fix (Windows PowerShell as Admin)**:
```powershell
icacls "C:\Workshopsntigravity-workshop-telecom" /grant "<AttendeeUser>:(OI)(CI)M" /T
```

---

## 6. 10-Point Pre-Workshop Verification Checklist for IT Admins

Run `./admin_requirements/admin_provision_workstation.sh --verify-only` as the **standard (non-admin) attendee user** and confirm all 10 checks pass:

1. `python3 --version` returns `Python 3.10+` (`3.11` or `3.12` recommended).
2. `uv --version` returns `uv 0.5+`.
3. `git --version` and `sqlite3 --version` return valid versions from `PATH`.
4. `terraform -version` and `gcloud --version` are available in `PATH` (for Lab 4).
5. Google Antigravity (`Antigravity 2.0`, `Antigravity IDE`, and/or `agy` CLI) opens and authenticates cleanly.
6. `./.venv/bin/python -c "import fastapi, uvicorn, pydantic, pytest, httpx, mcp, google.adk, google.genai"` exits with code `0`.
7. `./.venv/bin/adk --version` (or `./scripts/run_adk_web.sh --check`) succeeds with code `0`.
8. Running `./install.sh` prints `[OK] Pre-provisioned .venv detected with all required packages (zero-install mode)` and seeds `data/*.db` without errors.
9. Running `./verify.sh` (after applying solutions or during admin test) passes 100% of unit and integration tests (`21 passed` in Telecom / `20 passed` in Retail).
10. Localhost TCP ports `8001`, `8002`, and `8080` can be bound by the standard user without firewall prompts.
