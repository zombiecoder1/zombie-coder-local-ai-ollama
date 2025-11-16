# ZombieCoderAI Windows Service Installer
# This script installs the ZombieCoderAI provider as a Windows service using NSSM

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "❌ This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "🤖 Installing ZombieCoderAI Windows Service" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Define paths
$NSSM_PATH = "C:\tools\nssm\nssm.exe"
$PYTHON_PATH = "C:\model\.venv\Scripts\python.exe"
$MODEL_PATH = "C:\model"
$UVICORN_COMMAND = "-m uvicorn model_server:app --host 0.0.0.0 --port 8007"

# Check if NSSM exists
if (-not (Test-Path $NSSM_PATH)) {
    Write-Host "⚠️  NSSM not found at $NSSM_PATH" -ForegroundColor Yellow
    Write-Host "Please download NSSM and place it at C:\tools\nssm\nssm.exe" -ForegroundColor Yellow
    Write-Host "Download from: https://nssm.cc/download" -ForegroundColor Cyan
    exit 1
}

# Check if Python virtual environment exists
if (-not (Test-Path $PYTHON_PATH)) {
    Write-Host "❌ Python virtual environment not found at $PYTHON_PATH" -ForegroundColor Red
    exit 1
}

# Check if model_server.py exists
if (-not (Test-Path "$MODEL_PATH\model_server.py")) {
    Write-Host "❌ model_server.py not found at $MODEL_PATH\model_server.py" -ForegroundColor Red
    exit 1
}

# Install the service
Write-Host "🔧 Installing service..." -ForegroundColor Cyan
& $NSSM_PATH install ZombieCoderAI $PYTHON_PATH $UVICORN_COMMAND

# Set recovery options
Write-Host "🔧 Setting recovery options..." -ForegroundColor Cyan
& $NSSM_PATH set ZombieCoderAI AppDirectory $MODEL_PATH
& $NSSM_PATH set ZombieCoderAI AppRestartDelay 5000
& $NSSM_PATH set ZombieCoderAI Description "ZombieCoderAI Provider Ecosystem Server"

# Start the service
Write-Host "🚀 Starting service..." -ForegroundColor Cyan
& $NSSM_PATH start ZombieCoderAI

Write-Host "✅ ZombieCoderAI service installation completed!" -ForegroundColor Green
Write-Host "Use 'nssm start ZombieCoderAI' to start the service" -ForegroundColor Yellow
Write-Host "Use 'nssm stop ZombieCoderAI' to stop the service" -ForegroundColor Yellow
Write-Host "Use 'nssm status ZombieCoderAI' to check service status" -ForegroundColor Yellow