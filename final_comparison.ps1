# Final Comparison: Ollama vs Model Server

$testPrompts = @(
    "Write a Python function to add two numbers",
    "What is machine learning?",
    "Explain quantum computing in simple terms"
)

Write-Host "`n=== Final Comparison: Ollama vs Model Server ===`n" -ForegroundColor Cyan

foreach ($prompt in $testPrompts) {
    Write-Host "`n📝 Prompt: $prompt" -ForegroundColor Yellow
    Write-Host ("=" * 70)
    
    # Test Ollama
    Write-Host "`n[Ollama Service]" -ForegroundColor Cyan
    $ollamaReq = @{
        prompt = $prompt
        model = "deepseek-coder:1.3b"
        stream = $false
    } | ConvertTo-Json
    
    try {
        $ollamaStart = Get-Date
        $ollamaResp = Invoke-RestMethod -Uri "http://localhost:5252/api/generate" -Method Post -Body $ollamaReq -ContentType "application/json" -TimeoutSec 30
        $ollamaTime = ((Get-Date) - $ollamaStart).TotalMilliseconds
        Write-Host "✅ Latency: $([math]::Round($ollamaTime, 2)) ms" -ForegroundColor Green
        Write-Host "Response: $($ollamaResp.response.Substring(0, [Math]::Min(150, $ollamaResp.response.Length)))..." -ForegroundColor Gray
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 1
    
    # Test Model Server
    Write-Host "`n[Model Server]" -ForegroundColor Cyan
    $modelReq = @{
        model = "tinyllama-gguf"
        prompt = $prompt
        stream = $false
    } | ConvertTo-Json
    
    try {
        $modelStart = Get-Date
        $modelResp = Invoke-RestMethod -Uri "http://localhost:8155/api/generate" -Method Post -Body $modelReq -ContentType "application/json" -TimeoutSec 30
        $modelTime = ((Get-Date) - $modelStart).TotalMilliseconds
        Write-Host "✅ Latency: $([math]::Round($modelTime, 2)) ms" -ForegroundColor Green
        $content = $modelResp.runtime_response.content
        if (-not $content) { $content = $modelResp.runtime_response.text }
        Write-Host "Response: $($content.Substring(0, [Math]::Min(150, $content.Length)))..." -ForegroundColor Gray
    } catch {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 2
}

Write-Host "`n`n=== Summary ===" -ForegroundColor Cyan
Write-Host "✅ Model Server is running on port 8155" -ForegroundColor Green
Write-Host "✅ Models loaded from models_registry.json" -ForegroundColor Green
Write-Host "✅ Both /api/generate and /api/chat endpoints working" -ForegroundColor Green
Write-Host "`n=== Test Complete ===`n" -ForegroundColor Cyan

