$ErrorActionPreference = 'Stop'
param(
  [string]$DefaultModel = 'phi-2-gguf',
  [int]$Threads = 4,
  [string]$RuntimeBase = 'http://127.0.0.1:8155'
)

Write-Host "[AUTO] Checking runtime status..."
try {
  $rt = Invoke-RestMethod -TimeoutSec 5 -Method GET -Uri "$RuntimeBase/runtime/status"
} catch {
  Write-Host "[AUTO] Runtime status unavailable."; exit 1
}

$loaded = @()
if ($rt -and $rt.models) { $loaded = $rt.models | ForEach-Object { $_.model } }

if ($loaded.Count -gt 0) {
  Write-Host ("[AUTO] Model(s) already loaded: " + ($loaded -join ', '))
  exit 0
}

Write-Host "[AUTO] No models loaded. Loading default: $DefaultModel ..."
try {
  $resp = Invoke-WebRequest -UseBasicParsing -TimeoutSec 120 -Method POST -Uri "$RuntimeBase/runtime/load/$DefaultModel?threads=$Threads"
  Write-Host ("[AUTO] Load status: " + $resp.StatusCode)
} catch {
  Write-Host ("[AUTO] Load failed: " + $_.Exception.Message)
  exit 1
}

Write-Host "[AUTO] Done."

