#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-gcp-project-id}"
LOCATION="${GEMINI_ENTERPRISE_LOCATION:-global}"
APP_ID="${GEMINI_ENTERPRISE_APP_ID:-retail-pulse-gemini-enterprise-app}"
SERVICE_URL="${RETAIL_PULSE_PUBLIC_URL:-https://retail-pulse-omnichannel-uc.a.run.app}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --project)
      PROJECT_ID="$2"
      shift 2
      ;;
    --location)
      LOCATION="$2"
      shift 2
      ;;
    --app-id)
      APP_ID="$2"
      shift 2
      ;;
    --service-url)
      SERVICE_URL="$2"
      shift 2
      ;;
    *)
      echo "[ERROR] Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

DISCOVERY_ENDPOINT="https://discoveryengine.googleapis.com/v1alpha/projects/${PROJECT_ID}/locations/${LOCATION}/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents"

read -r -d '' AGENT_PAYLOAD <<EOF || true
{
  "displayName": "Retail Pulse ADK Multi-Agent Orchestrator",
  "description": "Omnichannel Order, True ATP Inventory Sync, Commercial Margin Floor & Supplier OTIF Chargeback Multi-Agent System (Delivered by Tryolabs).",
  "a2aAgentDefinition": {
    "agentCardUri": "${SERVICE_URL}/.well-known/agent.json",
    "endpointUri": "${SERVICE_URL}/api/v1/a2a"
  }
}
EOF

if [[ "$DRY_RUN" == "true" ]]; then
  echo "[DRY-RUN] Gemini Enterprise A2A Agent Registration Endpoint:"
  echo "  POST ${DISCOVERY_ENDPOINT}"
  echo "[DRY-RUN] Payload verified:"
  echo "${AGENT_PAYLOAD}"
  exit 0
fi

ACCESS_TOKEN="$(gcloud auth print-access-token)"
curl -sS -X POST "${DISCOVERY_ENDPOINT}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  -d "${AGENT_PAYLOAD}"
echo ""
echo "[OK] Registered Retail Pulse A2A Agent with Gemini Enterprise (${APP_ID})."
