#!/usr/bin/env bash
# ==============================================================================
# Tryolabs — Google Antigravity Workshop: IT Admin Workstation Provisioner
# Target OS: macOS (13+) & Linux (Ubuntu 22.04+, Debian 12+, RHEL 9+)
#
# Purpose:
#   Pre-provisions and verifies an attendee workstation so that an unprivileged
#   attendee (with NO sudo/admin rights and NO package install permissions) can
#   complete all 4 hands-on labs (Telecom Nexus & Retail Pulse).
#
# Usage (as IT Admin / root or standard check):
#   sudo ./admin_provision_workstation.sh --user <attendee_username>
#   ./admin_provision_workstation.sh --verify-only
# ==============================================================================
set -euo pipefail

ATTENDEE_USER="${SUDO_USER:-$(whoami)}"
VERIFY_ONLY=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user)
      ATTENDEE_USER="$2"
      shift 2
      ;;
    --verify-only)
      VERIFY_ONLY=1
      shift
      ;;
    *)
      shift
      ;;
  esac
done

echo "======================================================================"
echo "  Tryolabs • Google Antigravity Workshop — IT Admin Workstation Audit"
echo "  Target Attendee Account : ${ATTENDEE_USER}"
echo "  Mode                    : $( [[ $VERIFY_ONLY -eq 1 ]] && echo 'VERIFY ONLY' || echo 'PROVISION & VERIFY' )"
echo "======================================================================"

PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

check_bin() {
  local name="$1"
  local min_desc="$2"
  local required="$3"
  if command -v "$name" >/dev/null 2>&1; then
    local ver
    ver="$("$name" --version 2>&1 | head -n 1 || true)"
    echo "  [OK]   ${name} found (${min_desc}): ${ver}"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    if [[ "$required" == "REQUIRED" ]]; then
      echo "  [FAIL] ${name} MISSING (${min_desc}) — Required for Labs 1-4!"
      FAIL_COUNT=$((FAIL_COUNT + 1))
    else
      echo "  [WARN] ${name} not found in PATH (${min_desc})"
      WARN_COUNT=$((WARN_COUNT + 1))
    fi
  fi
}

echo ""
echo "[Step 1/4] Auditing System Binaries & CLI Tools in PATH..."
check_bin "python3"   "Python >= 3.10 (3.11/3.12 recommended)" "REQUIRED"
check_bin "uv"        "Astral uv >= 0.5.0 package manager"     "REQUIRED"
check_bin "git"       "Git CLI >= 2.39"                        "REQUIRED"
check_bin "sqlite3"   "SQLite3 CLI >= 3.37"                    "REQUIRED"
check_bin "bash"      "GNU Bash shell"                         "REQUIRED"
check_bin "curl"      "cURL HTTP CLI"                          "REQUIRED"
check_bin "terraform" "HashiCorp Terraform >= 1.5 (Lab 4 IaC)" "OPTIONAL"
check_bin "gcloud"    "Google Cloud SDK (Gemini Enterprise)"   "OPTIONAL"
check_bin "agy"       "Google Antigravity CLI (agy)"           "OPTIONAL"

echo ""
echo "[Step 2/4] Auditing Python Standard Library Modules (venv, sqlite3, decimal)..."
if python3 -c "import venv, sqlite3, decimal, json, pathlib; print('  [OK]   Python stdlib modules verified (SQLite ' + sqlite3.sqlite_version + ')')" 2>/dev/null; then
  PASS_COUNT=$((PASS_COUNT + 1))
else
  echo "  [FAIL] Python3 is missing standard modules (venv or sqlite3)!"
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

provision_repo() {
  local repo_dir="$1"
  if [[ ! -d "$repo_dir" ]] || [[ ! -f "$repo_dir/requirements.txt" ]]; then
    return 0
  fi
  echo ""
  echo "----------------------------------------------------------------------"
  echo "  Processing Workshop Repository: $repo_dir"
  echo "----------------------------------------------------------------------"
  cd "$repo_dir"

  if [[ $VERIFY_ONLY -eq 0 ]]; then
    if [[ ! -d ".venv" ]]; then
      echo "  -> Creating virtual environment (.venv)..."
      if command -v uv >/dev/null 2>&1; then
        uv venv .venv
      else
        python3 -m venv .venv
      fi
    fi

    echo "  -> Installing Python libraries into .venv..."
    if [[ -d "wheelhouse" ]]; then
      ./.venv/bin/pip install --quiet --no-index --find-links ./wheelhouse -r requirements.txt
    elif command -v uv >/dev/null 2>&1; then
      uv pip install --python ./.venv/bin/python -r requirements.txt
    else
      ./.venv/bin/pip install --quiet --upgrade pip
      ./.venv/bin/pip install --quiet -r requirements.txt
    fi

    echo "  -> Running initial database seed & Lab 01 starter state..."
    bash ./install.sh
  fi

  echo "  -> Verifying all required Python packages inside $repo_dir/.venv..."
  if ./.venv/bin/python -c "
import fastapi, uvicorn, pydantic, pytest, httpx, mcp, google.adk, google.genai, aiosqlite, starlette, sse_starlette, websockets, yaml, dotenv
print('  [OK]   All workshop Python packages imported successfully!')
"; then
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "  [FAIL] Missing Python libraries in $repo_dir/.venv!"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi

  echo "  -> Verifying CLI entrypoints in .venv/bin (pytest, uvicorn, adk)..."
  for ep in pytest uvicorn adk; do
    if [[ -x "./.venv/bin/$ep" ]]; then
      echo "  [OK]   ./.venv/bin/$ep is executable"
      PASS_COUNT=$((PASS_COUNT + 1))
    else
      echo "  [FAIL] ./.venv/bin/$ep is missing or not executable!"
      FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
  done

  if [[ $VERIFY_ONLY -eq 0 ]] && [[ "$(id -u)" -eq 0 ]] && id "$ATTENDEE_USER" >/dev/null 2>&1; then
    local primary_grp
    primary_grp="$(id -gn "$ATTENDEE_USER")"
    echo "  -> Granting full user ownership (${ATTENDEE_USER}:${primary_grp}) to $repo_dir..."
    chown -R "${ATTENDEE_USER}:${primary_grp}" "$repo_dir"
    chmod -R u+rwX "$repo_dir"
    echo "  [OK]   Non-admin attendee user '${ATTENDEE_USER}' now has full read/write permissions."
  fi
}

echo ""
echo "[Step 3/4] Provisioning & Verifying Workshop Repositories..."
# Check if script is inside a repo or parent workspace
if [[ -f "$SCRIPT_DIR/requirements.txt" ]] && [[ -d "$SCRIPT_DIR/labs" ]]; then
  provision_repo "$SCRIPT_DIR"
elif [[ -f "$SCRIPT_DIR/../requirements.txt" ]] && [[ -d "$SCRIPT_DIR/../labs" ]]; then
  provision_repo "$(cd "$SCRIPT_DIR/.." && pwd)"
fi

for candidate in   "$SCRIPT_DIR/antigravity-workshop-telecom"   "$SCRIPT_DIR/antigravity-workshop-retail"   "$SCRIPT_DIR/../antigravity-workshop-telecom"   "$SCRIPT_DIR/../antigravity-workshop-retail"; do
  if [[ -d "$candidate" ]]; then
    provision_repo "$(cd "$candidate" && pwd)"
  fi
done

echo ""
echo "[Step 4/4] Auditing Local Loopback Ports (8001, 8002, 8080)..."
python3 -c "
import socket
for port in (8001, 8002, 8080):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('127.0.0.1', port))
        print(f'  [OK]   Localhost TCP port 127.0.0.1:{port} is available for unprivileged binding')
    except OSError as e:
        print(f'  [WARN] Localhost TCP port 127.0.0.1:{port} is currently in use ({e})')
    finally:
        s.close()
"

echo ""
echo "======================================================================"
echo "  Summary: ${PASS_COUNT} checks passed | ${WARN_COUNT} warnings | ${FAIL_COUNT} failures"
if [[ $FAIL_COUNT -eq 0 ]]; then
  echo "  [READY] Workstation is 100% ready for non-admin workshop attendees!"
else
  echo "  [ACTION NEEDED] Please resolve the ${FAIL_COUNT} failed check(s) above."
  exit 1
fi
echo "======================================================================"
