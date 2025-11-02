$ErrorActionPreference = 'Stop'

Write-Host "[TEST] /health and /models/installed"

try {
    if (Test-Path "$PSScriptRoot/../../.venv/Scripts/Activate.ps1") {
        & "$PSScriptRoot/../../.venv/Scripts/Activate.ps1"
    }
} catch {}

function Show-Response($label, $resp) {
    Write-Host ("[STATUS] " + $label + ": " + $resp.StatusCode)
    try {
        $json = $resp.Content | ConvertFrom-Json
        $json | ConvertTo-Json -Depth 6
    } catch {
        Write-Host $resp.Content
    }
}

try {
    $h = Invoke-WebRequest -UseBasicParsing -TimeoutSec 10 http://127.0.0.1:8007/health
    Show-Response "/health" $h
} catch { Write-Host "[ERROR] /health failed: $_" }

try {
    $m = Invoke-WebRequest -UseBasicParsing -TimeoutSec 15 http://127.0.0.1:8007/models/installed
    Show-Response "/models/installed" $m
} catch { Write-Host "[ERROR] /models/installed failed: $_" }

Write-Host "[DONE] health/models checks"

