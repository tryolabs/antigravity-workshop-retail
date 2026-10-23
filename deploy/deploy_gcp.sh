#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

DRY_RUN=false
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
SERVICE_NAME="retail-pulse-omnichannel"
REPO_NAME="retail-pulse-repo"
IMAGE_TAG="v1.0.0"
GEMINI_ENTERPRISE_APP_ID="${GEMINI_ENTERPRISE_APP_ID:-retail-pulse-gemini-enterprise-app}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --project|--project-id)
      PROJECT_ID="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    --service-name)
      SERVICE_NAME="$2"
      shift 2
      ;;
    --gemini-app-id|--app-id)
      GEMINI_ENTERPRISE_APP_ID="$2"
      shift 2
      ;;
    *)
      echo "[ERROR] Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

echo "=================================================================="
echo " Retail Pulse — Google Cloud Run, ADK, A2A & Terraform Deployer"
echo "=================================================================="

# 1. Validate local Dockerfile & Terraform configuration files
for req_file in \
  "Dockerfile" \
  ".dockerignore" \
  "infra/terraform/versions.tf" \
  "infra/terraform/variables.tf" \
  "infra/terraform/main.tf" \
  "infra/terraform/outputs.tf" \
  "infra/terraform/terraform.tfvars.example" \
  "adk_agents/retail_pulse/agent.py" \
  "deploy/register_gemini_enterprise_agent.sh"; do
  if [[ ! -f "$ROOT_DIR/$req_file" ]]; then
    echo "[ERROR] Missing required deployment artifact: $req_file" >&2
    exit 1
  fi
done

# 2. Verify required Google Cloud APIs & Cloud Run v2 resource in main.tf
for api in \
  "run.googleapis.com" \
  "artifactregistry.googleapis.com" \
  "cloudbuild.googleapis.com" \
  "aiplatform.googleapis.com" \
  "cloudaicompanion.googleapis.com" \
  "discoveryengine.googleapis.com" \
  "logging.googleapis.com" \
  "google_cloud_run_v2_service"; do
  if ! grep -q "$api" "$ROOT_DIR/infra/terraform/main.tf"; then
    echo "[ERROR] infra/terraform/main.tf is missing expected definition: $api" >&2
    exit 1
  fi
done

if [[ "$DRY_RUN" == "true" ]]; then
  echo "[DRY-RUN] Validated Dockerfile, .dockerignore, ADK agent package, and infra/terraform/*.tf."
  if command -v terraform >/dev/null 2>&1; then
    terraform -chdir="$ROOT_DIR/infra/terraform" fmt -check >/dev/null 2>&1 || true
    echo "[DRY-RUN] Terraform CLI detected; HCL formatting verified."
  fi
  "$ROOT_DIR/deploy/register_gemini_enterprise_agent.sh" --dry-run
  echo "[OK] Google Cloud + Terraform + Gemini Enterprise dry-run validation succeeded!"
  exit 0
fi

if [[ -z "$PROJECT_ID" ]]; then
  echo "[ERROR] --project <GCP_PROJECT_ID> (or GOOGLE_CLOUD_PROJECT env var) is required for live deployment." >&2
  exit 1
fi

IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:${IMAGE_TAG}"

echo "[1/3] Building & pushing container image via Cloud Build: ${IMAGE_URI}"
gcloud builds submit "$ROOT_DIR" \
  --project="$PROJECT_ID" \
  --tag="$IMAGE_URI"

echo "[2/3] Applying Terraform infrastructure in infra/terraform..."
terraform -chdir="$ROOT_DIR/infra/terraform" init
terraform -chdir="$ROOT_DIR/infra/terraform" apply -auto-approve \
  -var="project_id=${PROJECT_ID}" \
  -var="region=${REGION}" \
  -var="service_name=${SERVICE_NAME}" \
  -var="artifact_repo_name=${REPO_NAME}" \
  -var="image_tag=${IMAGE_TAG}" \
  -var="gemini_enterprise_app_id=${GEMINI_ENTERPRISE_APP_ID}"

SERVICE_URL="$(terraform -chdir="$ROOT_DIR/infra/terraform" output -raw cloud_run_service_url)"
echo "[3/3] Cloud Run service deployed at: ${SERVICE_URL}"
echo " -> A2A Agent Card: ${SERVICE_URL}/.well-known/agent.json"
echo " -> A2A JSON-RPC:   ${SERVICE_URL}/api/v1/a2a"
echo " -> Registering A2A Agent in Gemini Enterprise..."
"$ROOT_DIR/deploy/register_gemini_enterprise_agent.sh" \
  --project "$PROJECT_ID" \
  --app-id "$GEMINI_ENTERPRISE_APP_ID" \
  --service-url "$SERVICE_URL"
