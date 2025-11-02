$ErrorActionPreference = 'Stop'

Write-Host "[ENV] Starting environment and ports check..."

try {
    if (Test-Path "$PSScriptRoot/../../.venv/Scripts/Activate.ps1") {
        & "$PSScriptRoot/../../.venv/Scripts/Activate.ps1"
        Write-Host "[ENV] Virtual environment activated"
    } else {
        Write-Host "[ENV] Virtual environment not found at .venv"
    }
} catch { Write-Host "[ENV] venv activation failed: $_" }

try { Write-Host ("[ENV] PowerShell: " + ($PSVersionTable.PSVersion.ToString())) } catch {}
try { Write-Host ("[ENV] Python: " + (& python -V 2>&1)) } catch { Write-Host "[ENV] Python not found" }

Write-Host "[PORTS] Listing 8007, 8155, 12346"
& netstat -ano | findstr :8007
& netstat -ano | findstr :8155
& netstat -ano | findstr :12346

Write-Host "[HEALTH] Probing 8007 /health and 8155 /ui and 12346 /"
try { $r1 = Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 http://127.0.0.1:8007/health; Write-Host ("[HEALTH] 8007 /health: " + $r1.StatusCode) } catch { Write-Host "[HEALTH] 8007 /health: FAIL" }
try { $r2 = Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 http://127.0.0.1:8155/ui; Write-Host ("[HEALTH] 8155 /ui: " + $r2.StatusCode) } catch { Write-Host "[HEALTH] 8155 /ui: FAIL" }
try { $r3 = Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 http://127.0.0.1:12346/; Write-Host ("[HEALTH] 12346 /: " + $r3.StatusCode) } catch { Write-Host "[HEALTH] 12346 /: FAIL" }

Write-Host "[DONE] Environment and ports check completed"

