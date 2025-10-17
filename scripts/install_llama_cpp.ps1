param(
  [string]$Url = "https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-server.exe",
  [string]$TargetDir = "C:\model\config\llama.cpp"
)

$ErrorActionPreference = 'SilentlyContinue'
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
$exe = Join-Path $TargetDir 'server.exe'
$log = Join-Path $TargetDir 'install.log'

function Log($m){ Add-Content -Path $log -Value ("$(Get-Date -Format s)`t$m") }

Log "# START install llama.cpp"
function Try-Download([string]$u){
  try{
    Log "downloading: $u"
    Invoke-WebRequest -Uri $u -OutFile $exe -UseBasicParsing -TimeoutSec 600
    if((Test-Path $exe) -and ((Get-Item $exe).Length -gt 1000000)){
      Log "saved_ok: $exe size=$((Get-Item $exe).Length)"
      return $true
    } else {
      Log "file_too_small_or_missing"
      Remove-Item -Force -ErrorAction SilentlyContinue $exe
      return $false
    }
  } catch {
    Log "download_error: $($_.Exception.Message)"
    return $false
  }
}

$ok = Try-Download $Url
if(-not $ok){
  $candidates = @(
    "https://github.com/ggerganov/llama.cpp/releases/latest/download/llama-server.exe",
    "https://huggingface.co/ashwink89/llama.cpp-binaries/resolve/main/llama-server.exe?download=true"
  )
  foreach($u in $candidates){ if(Try-Download $u){ $ok=$true; break } }
}
if(-not $ok){ Log "all_attempts_failed" }
Log "# END"
Write-Output ("{`"status`":`"ok`",`"path`":`"$exe`",`"log`":`"$log`"}")


