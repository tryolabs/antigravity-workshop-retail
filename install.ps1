$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RootDir

Write-Host "=================================================================="
Write-Host " Retail Pulse: Google Antigravity Retail Workshop Installer (Win)"
Write-Host "=================================================================="

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python data/seed_retail_data.py

Write-Host ""
Write-Host "[OK] Retail Pulse environment ready!"
Write-Host " -> Run Web Dashboard: .\.venv\Scripts\uvicorn src.main:app --reload --port 8002"
Write-Host " -> Start Lab 1:       .\labs\lab-01-margin-inventory-triage\install.ps1"
