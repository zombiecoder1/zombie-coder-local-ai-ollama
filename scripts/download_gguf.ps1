param(
  [Parameter(Mandatory=$true)][string]$RepoId,
  [Parameter(Mandatory=$true)][string]$ModelName,
  [string]$Revision = $null
)

$ErrorActionPreference = 'SilentlyContinue'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$modelsDir = Join-Path (Split-Path -Parent $root) 'models'
New-Item -ItemType Directory -Force -Path $modelsDir | Out-Null
$targetDir = Join-Path $modelsDir $ModelName
New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
$log = Join-Path $modelsDir ("download_" + $ModelName + ".log")

function Write-Log($msg){
  $ts = (Get-Date).ToString('s')
  Add-Content -Path $log -Value ("$ts`t$msg")
}

Write-Log "# START repo=$RepoId model=$ModelName rev=$Revision"

# Try hf download if available
$hf = (Get-Command hf -ErrorAction SilentlyContinue).Source
if($hf){
  Write-Log "using: hf download"
  $args = @('download', $RepoId, '--local-dir', $targetDir, '--local-dir-use-symlinks', 'False')
  if($Revision){ $args += @('--revision', $Revision) }
  Start-Process -FilePath $hf -ArgumentList $args -NoNewWindow -Wait -RedirectStandardOutput $log -RedirectStandardError $log
}
else{
  $cli = (Get-Command huggingface-cli -ErrorAction SilentlyContinue).Source
  if($cli){
    Write-Log "using: huggingface-cli download"
    $args = @('download', $RepoId, '--local-dir', $targetDir, '--local-dir-use-symlinks', 'False')
    if($Revision){ $args += @('--revision', $Revision) }
    Start-Process -FilePath $cli -ArgumentList $args -NoNewWindow -Wait -RedirectStandardOutput $log -RedirectStandardError $log
  }
  else{
    Write-Log "fallback: python snapshot_download"
    $py = @'
import sys, json
from pathlib import Path
from huggingface_hub import snapshot_download
repo_id = sys.argv[1]
target = sys.argv[2]
rev = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != 'None' else None
local_path = snapshot_download(repo_id=repo_id, revision=rev, local_dir=target, local_dir_use_symlinks=False,
                               allow_patterns=['*.gguf','*.safetensors','*.bin','*.json','tokenizer*','config*'])
print(json.dumps({'ok': True, 'path': local_path}))
'@
    & python -c $py $RepoId $targetDir $Revision 1>> $log 2>> $log
  }
}

Write-Log "# END"
Write-Output ("{`"status`":`"done`",`"target_dir`":`"$targetDir`",`"log`":`"$log`"}")


