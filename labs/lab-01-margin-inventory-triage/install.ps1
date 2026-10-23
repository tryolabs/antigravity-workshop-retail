$ErrorActionPreference = "Stop"
$LabDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Resolve-Path "$LabDir\..\.."
Set-Location $RootDir

if (-not (Test-Path ".venv")) {
    & "$RootDir\install.ps1"
}

Copy-Item "$LabDir\starter\promo_pricing.py" "$RootDir\src\services\promo_pricing.py" -Force
Copy-Item "$LabDir\starter\inventory_atp.py" "$RootDir\src\services\inventory_atp.py" -Force
Copy-Item "$RootDir\labs\lab-03-mcp-and-hooks\starter\retail_mcp.py" "$RootDir\mcp_server\retail_mcp.py" -Force
Copy-Item "$RootDir\labs\lab-04-multi-agent-capstone\starter\fulfillment_router.py" "$RootDir\src\services\fulfillment_router.py" -Force
Remove-Item "$RootDir\GEMINI.md" -ErrorAction SilentlyContinue
Remove-Item "$RootDir\.agents\rules\retail-standards.md" -ErrorAction SilentlyContinue
Remove-Item "$RootDir\.agents\skills\margin-otif-audit\SKILL.md" -ErrorAction SilentlyContinue
Remove-Item "$RootDir\.agents\mcp_config.json" -ErrorAction SilentlyContinue
Remove-Item "$RootDir\.agents\hooks.json" -ErrorAction SilentlyContinue

.\.venv\Scripts\python data/seed_retail_data.py | Out-Null
Write-Host "[Lab 01 Ready] Margin Floor & True ATP Inventory Triage initialized."
