$ErrorActionPreference = "Stop"
$LabDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Resolve-Path "$LabDir\..\.."
Set-Location $RootDir

if (-not (Test-Path ".venv")) {
    & "$RootDir\install.ps1"
}

Copy-Item "$RootDir\labs\lab-01-margin-inventory-triage\solution\promo_pricing.py" "$RootDir\src\services\promo_pricing.py" -Force
Copy-Item "$RootDir\labs\lab-01-margin-inventory-triage\solution\inventory_atp.py" "$RootDir\src\services\inventory_atp.py" -Force
Remove-Item "$RootDir\GEMINI.md" -ErrorAction SilentlyContinue
Remove-Item "$RootDir\.agents\rules\retail-standards.md" -ErrorAction SilentlyContinue
Remove-Item "$RootDir\.agents\skills\margin-otif-audit\SKILL.md" -ErrorAction SilentlyContinue

Write-Host "[Lab 02 Ready] Prerequisite Lab 01 solution applied; Lab 02 initialized."
