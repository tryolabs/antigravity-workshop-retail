$ErrorActionPreference = "Stop"
$LabDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Resolve-Path "$LabDir\..\.."
Set-Location $RootDir

if (-not (Test-Path ".venv")) {
    & "$RootDir\install.ps1"
}

Copy-Item "$RootDir\labs\lab-01-margin-inventory-triage\solution\promo_pricing.py" "$RootDir\src\services\promo_pricing.py" -Force
Copy-Item "$RootDir\labs\lab-01-margin-inventory-triage\solution\inventory_atp.py" "$RootDir\src\services\inventory_atp.py" -Force
New-Item -ItemType Directory -Force -Path "$RootDir\.agents\rules", "$RootDir\.agents\skills\margin-otif-audit" | Out-Null
Copy-Item "$RootDir\labs\lab-02-rules-and-skills\solution\GEMINI.md" "$RootDir\GEMINI.md" -Force
Copy-Item "$RootDir\labs\lab-02-rules-and-skills\solution\retail-standards.md" "$RootDir\.agents\rules\retail-standards.md" -Force
Copy-Item "$RootDir\labs\lab-02-rules-and-skills\solution\SKILL.md" "$RootDir\.agents\skills\margin-otif-audit\SKILL.md" -Force

Copy-Item "$LabDir\starter\retail_mcp.py" "$RootDir\mcp_server\retail_mcp.py" -Force
Remove-Item "$RootDir\.agents\mcp_config.json" -ErrorAction SilentlyContinue
Remove-Item "$RootDir\.agents\hooks.json" -ErrorAction SilentlyContinue

Write-Host "[Lab 03 Ready] Prerequisite Lab 01 & Lab 02 solutions applied; Lab 03 initialized."
