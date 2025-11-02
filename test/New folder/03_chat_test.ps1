$ErrorActionPreference = 'Stop'

Write-Host "[TEST] POST /api/chat"

try {
    if (Test-Path "$PSScriptRoot/../../.venv/Scripts/Activate.ps1") {
        & "$PSScriptRoot/../../.venv/Scripts/Activate.ps1"
    }
} catch {}

# Attempt a generic chat schema
$payload = @{ 
    model = 'phi-2-gguf';
    messages = @(
        @{ role = 'user'; content = 'Say hello in one short sentence.' }
    )
}
$json = $payload | ConvertTo-Json -Depth 6

try {
    $resp = Invoke-WebRequest -UseBasicParsing -TimeoutSec 120 -Method POST -Uri http://127.0.0.1:8007/api/chat -ContentType 'application/json' -Body $json
    Write-Host ("[STATUS] /api/chat: " + $resp.StatusCode)
    try { $obj = $resp.Content | ConvertFrom-Json; $obj | ConvertTo-Json -Depth 6 } catch { Write-Host $resp.Content }
} catch { Write-Host "[ERROR] /api/chat failed: $_" }

Write-Host "[DONE] chat test"

