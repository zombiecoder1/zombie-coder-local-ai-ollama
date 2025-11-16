# NSSM and ZombieCoderAI Service Installer
# This script downloads NSSM and installs the ZombieCoderAI provider as a Windows service

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "❌ This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "🤖 Installing NSSM and ZombieCoderAI Windows Service" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Define paths
$TOOLS_DIR = "C:\tools"
$NSSM_DIR = "$TOOLS_DIR\nssm"
$NSSM_PATH = "$NSSM_DIR\nssm.exe"
$PYTHON_PATH = "C:\model\.venv\Scripts\python.exe"
$MODEL_PATH = "C:\model"
$UVICORN_COMMAND = "-m uvicorn model_server:app --host 0.0.0.0 --port 8007"

# Create tools directory if it doesn't exist
if (-not (Test-Path $TOOLS_DIR)) {
    Write-Host "🔧 Creating tools directory..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $TOOLS_DIR | Out-Null
}

# Check if NSSM already exists
if (Test-Path $NSSM_PATH) {
    Write-Host "✅ NSSM already installed at $NSSM_PATH" -ForegroundColor Green
} else {
    Write-Host "🔧 Downloading NSSM..." -ForegroundColor Cyan
    
    # Download NSSM
    $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $zipPath = "$TOOLS_DIR\nssm.zip"
    
    try {
        Invoke-WebRequest -Uri $nssmUrl -OutFile $zipPath
        Write-Host "✅ NSSM downloaded successfully" -ForegroundColor Green
        
        # Extract NSSM
        Write-Host "🔧 Extracting NSSM..." -ForegroundColor Cyan
        Expand-Archive -Path $zipPath -DestinationPath $TOOLS_DIR -Force
        
        # Find the extracted NSSM directory (it might have version in the name)
        $extractedDirs = Get-ChildItem -Path $TOOLS_DIR -Directory | Where-Object { $_.Name -like "nssm*" }
        if ($extractedDirs.Count -gt 0) {
            $extractedDir = $extractedDirs[0].FullName
            # Move the contents to our standard location
            if (Test-Path $NSSM_DIR) {
                Remove-Item -Path $NSSM_DIR -Recurse -Force
            }
            Move-Item -Path "$extractedDir\win64" -Destination $NSSM_DIR
            Write-Host "✅ NSSM extracted to $NSSM_DIR" -ForegroundColor Green
        }
        
        # Clean up
        Remove-Item -Path $zipPath -Force
        if (Test-Path $extractedDir) {
            Remove-Item -Path $extractedDir -Recurse -Force
        }
    } catch {
        Write-Host "❌ Failed to download/extract NSSM: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please download NSSM manually from https://nssm.cc/download and place it at C:\tools\nssm\nssm.exe" -ForegroundColor Yellow
        exit 1
    }
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
Write-Host "🔧 Installing ZombieCoderAI service..." -ForegroundColor Cyan
& $NSSM_PATH install ZombieCoderAI $PYTHON_PATH $UVICORN_COMMAND

# Set recovery options
Write-Host "🔧 Setting recovery options..." -ForegroundColor Cyan
& $NSSM_PATH set ZombieCoderAI AppDirectory $MODEL_PATH
& $NSSM_PATH set ZombieCoderAI AppRestartDelay 5000
& $NSSM_PATH set ZombieCoderAI Description "ZombieCoderAI Provider Ecosystem Server"

# Set additional options
& $NSSM_PATH set ZombieCoderAI AppStdout "$MODEL_PATH\logs\zombiecoder_stdout.log"
& $NSSM_PATH set ZombieCoderAI AppStderr "$MODEL_PATH\logs\zombiecoder_stderr.log"

Write-Host "✅ NSSM installation and service setup completed!" -ForegroundColor Green
Write-Host "Use 'nssm start ZombieCoderAI' to start the service" -ForegroundColor Yellow
Write-Host "Use 'nssm stop ZombieCoderAI' to stop the service" -ForegroundColor Yellow
Write-Host "Use 'nssm status ZombieCoderAI' to check service status" -ForegroundColor Yellow