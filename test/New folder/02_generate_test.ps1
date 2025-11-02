$ErrorActionPreference = 'Stop'

Write-Host "[TEST] POST /api/generate"

try {
    if (Test-Path "$PSScriptRoot/../../.venv/Scripts/Activate.ps1") {
        & "$PSScriptRoot/../../.venv/Scripts/Activate.ps1"
    }
} catch {}

$body = @{ model = 'phi-2-gguf'; prompt = 'Hello! Please introduce yourself in one sentence.' }
$json = $body | ConvertTo-Json -Depth 5

try {
    $resp = Invoke-WebRequest -UseBasicParsing -TimeoutSec 120 -Method POST -Uri http://127.0.0.1:8007/api/generate -ContentType 'application/json' -Body $json
    Write-Host ("[STATUS] /api/generate: " + $resp.StatusCode)
    try { $obj = $resp.Content | ConvertFrom-Json; $obj | ConvertTo-Json -Depth 6 } catch { Write-Host $resp.Content }
} catch { Write-Host "[ERROR] /api/generate failed: $_" }

Write-Host "[DONE] generate test"

