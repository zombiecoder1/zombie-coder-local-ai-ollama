# Force cleanup script for model directories
Write-Host "Force Cleanup Script for Model Directories"
Write-Host "=========================================="

# Models to remove
$modelsToRemove = @("deepseek-coder-1.3b", "tinyllama-gguf")

foreach ($model in $modelsToRemove) {
    $path = "models\$model"
    if (Test-Path $path) {
        Write-Host "Attempting to remove $path..."
        try {
            # Try to remove with force
            Remove-Item -Path $path -Recurse -Force -ErrorAction Stop
            Write-Host "Successfully removed $path"
        } catch {
            Write-Host "Failed to remove $path : $($_.Exception.Message)"
        }
    } else {
        Write-Host "Path not found: $path"
    }
}

Write-Host "Cleanup attempt completed."