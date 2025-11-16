# ZombieCoderAI Service Installer
# This script installs the ZombieCoderAI provider as a Windows service using NSSM

Write-Host "🤖 ZombieCoderAI Service Installation" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

# Check if NSSM is installed and get its path
$nssmPath = $null
try {
    $nssmPath = (Get-Command nssm).Source
    Write-Host "✅ Found NSSM at: $nssmPath" -ForegroundColor Green
} catch {
    Write-Host "❌ NSSM not found in PATH" -ForegroundColor Red
    Write-Host "Please install NSSM first:" -ForegroundColor Yellow
    Write-Host "1. Download NSSM from https://nssm.cc/download" -ForegroundColor Yellow
    Write-Host "2. Extract and place nssm.exe at C:\tools\nssm\nssm.exe" -ForegroundColor Yellow
    Write-Host "3. Or install NSSM using Chocolatey: choco install nssm" -ForegroundColor Yellow
    exit 1
}

# Define paths
$PYTHON_PATH = "C:\model\.venv\Scripts\python.exe"
$MODEL_PATH = "C:\model"
$UVICORN_COMMAND = "-m uvicorn model_server:app --host 0.0.0.0 --port 8007"

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
Write-Host "🔧 Installing ZombieCoderAI service..." -ForegroundColor Cyan
& $nssmPath install ZombieCoderAI $PYTHON_PATH $UVICORN_COMMAND

# Set recovery options
Write-Host "🔧 Setting recovery options..." -ForegroundColor Cyan
& $nssmPath set ZombieCoderAI AppDirectory $MODEL_PATH
& $nssmPath set ZombieCoderAI AppRestartDelay 5000
& $nssmPath set ZombieCoderAI Description "ZombieCoderAI Provider Ecosystem Server"

# Set additional options
& $nssmPath set ZombieCoderAI AppStdout "$MODEL_PATH\logs\zombiecoder_stdout.log"
& $nssmPath set ZombieCoderAI AppStderr "$MODEL_PATH\logs\zombiecoder_stderr.log"

Write-Host "✅ ZombieCoderAI service installation completed!" -ForegroundColor Green
Write-Host "Use 'nssm start ZombieCoderAI' to start the service" -ForegroundColor Yellow
Write-Host "Use 'nssm stop ZombieCoderAI' to stop the service" -ForegroundColor Yellow
Write-Host "Use 'nssm status ZombieCoderAI' to check service status" -ForegroundColor Yellow