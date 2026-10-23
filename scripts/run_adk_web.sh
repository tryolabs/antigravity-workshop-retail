#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PORT="${ADK_WEB_PORT:-8080}"
HOST="${ADK_WEB_HOST:-127.0.0.1}"

if [[ "${1:-}" == "--dry-run" ]] || [[ "${1:-}" == "--check" ]]; then
  ./.venv/bin/python -c "from adk_agents.retail_pulse.agent import root_agent; assert root_agent.name == 'retail_pulse_root_agent'; print('[OK] ADK root_agent verified:', root_agent.name, 'with sub_agents:', [a.name for a in root_agent.sub_agents])"
  exit 0
fi

./.venv/bin/adk telemetry disable >/dev/null 2>&1 || true

echo "=================================================================="
echo " Launching Google ADK Development UI (adk web) — Retail Pulse"
echo " -> Agent Directory: $ROOT_DIR/adk_agents"
echo " -> Root Agent:      retail_pulse (retail_pulse_root_agent)"
echo " -> ADK Web UI URL:  http://${HOST}:${PORT}"
echo "=================================================================="

exec ./.venv/bin/adk web adk_agents \
  --host "$HOST" \
  --port "$PORT" \
  --logo-text "Retail Pulse ADK (Delivered by Tryolabs)"
