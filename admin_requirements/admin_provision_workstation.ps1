# ==============================================================================
# Tryolabs — Google Antigravity Workshop: IT Admin Workstation Provisioner
# Target OS: Windows 10 / 11 (64-bit) — Run in Elevated PowerShell (Admin)
#
# Purpose:
#   Pre-provisions and verifies a Windows attendee workstation so that an
#   unprivileged attendee (Standard User with NO admin rights) can complete
#   all 4 hands-on labs (Telecom Nexus & Retail Pulse).
#
# Usage:
#   .\admin_provision_workstation.ps1 -AttendeeUser "CORP\jdoe"
#   .\admin_provision_workstation.ps1 -VerifyOnly
# ==============================================================================
param(
    [string]$AttendeeUser = $env:USERNAME,
    [switch]$VerifyOnly = $false
)

$ErrorActionPreference = "Continue"
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Tryolabs • Google Antigravity Workshop — Windows IT Admin Provisioner" -ForegroundColor Cyan
Write-Host "  Target Attendee User : $AttendeeUser"
Write-Host "======================================================================" -ForegroundColor Cyan

$tools = @(
    @{ Name = "python";    Desc = "Python >= 3.10 (3.11/3.12 recommended)"; Req = $true },
    @{ Name = "uv";        Desc = "Astral uv >= 0.5.0 package manager";     Req = $true },
    @{ Name = "git";       Desc = "Git for Windows (with Git Bash)";        Req = $true },
    @{ Name = "sqlite3";   Desc = "SQLite3 CLI >= 3.37";                    Req = $true },
    @{ Name = "terraform"; Desc = "HashiCorp Terraform >= 1.5 (Lab 4)";     Req = $false },
    @{ Name = "gcloud";    Desc = "Google Cloud SDK (Gemini Enterprise)";   Req = $false },
    @{ Name = "agy";       Desc = "Google Antigravity CLI (agy)";           Req = $false }
)

Write-Host "`n[Step 1/3] Auditing System Binaries in PATH..." -ForegroundColor Yellow
foreach ($t in $tools) {
    $cmd = Get-Command $t.Name -ErrorAction SilentlyContinue
    if ($cmd) {
        Write-Host "  [OK]   $($t.Name) found ($($t.Desc)) -> $($cmd.Source)" -ForegroundColor Green
    } elseif ($t.Req) {
        Write-Host "  [FAIL] $($t.Name) MISSING ($($t.Desc)) — Required for Labs 1-4!" -ForegroundColor Red
    } else {
        Write-Host "  [WARN] $($t.Name) not found in PATH ($($t.Desc))" -ForegroundColor DarkYellow
    }
}

Write-Host "`n[Step 2/3] Provisioning Workshop Python Virtual Environment (.venv)..." -ForegroundColor Yellow
$RepoDirs = @(
    (Join-Path $PSScriptRoot ".."),
    (Join-Path $PSScriptRoot "..\antigravity-workshop-telecom"),
    (Join-Path $PSScriptRoot "..\antigravity-workshop-retail")
)

foreach ($dir in $RepoDirs) {
    $reqFile = Join-Path $dir "requirements.txt"
    if (Test-Path $reqFile) {
        $resolved = (Resolve-Path $dir).Path
        Write-Host "  -> Configuring repository: $resolved" -ForegroundColor Cyan
        Push-Location $resolved
        if (-not $VerifyOnly) {
            if (-not (Test-Path ".venv")) {
                if (Get-Command uv -ErrorAction SilentlyContinue) {
                    uv venv .venv
                } else {
                    python -m venv .venv
                }
            }
            if (Get-Command uv -ErrorAction SilentlyContinue) {
                uv pip install --python .\.venv\Scripts\python.exe -r requirements.txt
            } else {
                .\.venv\Scripts\pip.exe install --upgrade pip
                .\.venv\Scripts\pip.exe install -r requirements.txt
            }
            # Grant Modify permissions to the non-admin attendee user
            icacls "$resolved" /grant "${AttendeeUser}:(OI)(CI)M" /T /Q | Out-Null
            Write-Host "  [OK] Granted Modify permissions on $resolved to $AttendeeUser" -ForegroundColor Green
        }
        .\.venv\Scripts\python.exe -c "import fastapi, uvicorn, pydantic, pytest, httpx, mcp, google.adk, google.genai; print('  [OK] All workshop Python libraries verified!')"
        Pop-Location
    }
}

Write-Host "`n[Step 3/3] Workstation Audit Complete!" -ForegroundColor Green
