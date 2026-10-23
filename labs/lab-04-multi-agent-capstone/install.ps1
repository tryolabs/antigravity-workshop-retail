$ErrorActionPreference = "Stop"
$LabDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Resolve-Path "$LabDir\..\.."
Set-Location $RootDir

if (-not (Test-Path ".venv")) {
    & "$RootDir\install.ps1"
}

& "$RootDir\labs\lab-03-mcp-and-hooks\install.ps1"
Copy-Item "$RootDir\labs\lab-03-mcp-and-hooks\solution\retail_mcp.py" "$RootDir\mcp_server\retail_mcp.py" -Force
Copy-Item "$RootDir\labs\lab-03-mcp-and-hooks\solution\mcp_config.json" "$RootDir\.agents\mcp_config.json" -Force
Copy-Item "$RootDir\labs\lab-03-mcp-and-hooks\solution\hooks.json" "$RootDir\.agents\hooks.json" -Force
Copy-Item "$LabDir\starter\fulfillment_router.py" "$RootDir\src\services\fulfillment_router.py" -Force

Write-Host "[Lab 04 Ready] Prerequisite Lab 01, 02 & 03 solutions applied; Lab 04 initialized."
