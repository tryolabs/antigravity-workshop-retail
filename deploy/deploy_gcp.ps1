param(
    [switch]$DryRun = $false,
    [string]$Project = $env:GOOGLE_CLOUD_PROJECT,
    [string]$Region = "us-central1",
    [string]$ServiceName = "retail-pulse-omnichannel",
    [string]$RepoName = "retail-pulse-repo",
    [string]$ImageTag = "v1.0.0",
    [string]$GeminiAppId = "retail-pulse-gemini-enterprise-app"
)

$ErrorActionPreference = "Stop"
$RootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RootDir

$RequiredFiles = @(
    "Dockerfile",
    ".dockerignore",
    "infra/terraform/versions.tf",
    "infra/terraform/variables.tf",
    "infra/terraform/main.tf",
    "infra/terraform/outputs.tf",
    "infra/terraform/terraform.tfvars.example",
    "adk_agents/retail_pulse/agent.py",
    "deploy/register_gemini_enterprise_agent.sh"
)

foreach ($f in $RequiredFiles) {
    if (-not (Test-Path (Join-Path $RootDir $f))) {
        throw "Missing required deployment artifact: $f"
    }
}

if ($DryRun) {
    Write-Host "[DRY-RUN] Validated Dockerfile, ADK agent package, and infra/terraform/*.tf."
    Write-Host "[OK] Google Cloud + Terraform + Gemini Enterprise dry-run validation succeeded!"
    exit 0
}

if (-not $Project) {
    throw "Specify -Project <GCP_PROJECT_ID> or set GOOGLE_CLOUD_PROJECT for live deployment."
}

$ImageUri = "$Region-docker.pkg.dev/$Project/$RepoName/${ServiceName}:$ImageTag"
gcloud builds submit $RootDir --project=$Project --tag=$ImageUri
terraform -chdir="$RootDir/infra/terraform" init
terraform -chdir="$RootDir/infra/terraform" apply -auto-approve `
    -var="project_id=$Project" `
    -var="region=$Region" `
    -var="service_name=$ServiceName" `
    -var="artifact_repo_name=$RepoName" `
    -var="image_tag=$ImageTag" `
    -var="gemini_enterprise_app_id=$GeminiAppId"
