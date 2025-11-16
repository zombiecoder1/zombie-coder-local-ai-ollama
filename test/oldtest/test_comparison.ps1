# Compare Ollama vs Model Server Responses

$ollamaUrl = "http://localhost:5252/api/generate"
$modelServerUrl = "http://localhost:8155/api/generate"

$testPrompt = "Write a Python function to calculate factorial"

Write-Host "`n=== Testing Ollama Service ===`n" -ForegroundColor Cyan

# Test Ollama
$ollamaRequest = @{
    prompt = $testPrompt
    model = "deepseek-coder:1.3b"
    stream = $false
} | ConvertTo-Json

try {
    $ollamaStart = Get-Date
    $ollamaResponse = Invoke-RestMethod -Uri $ollamaUrl -Method Post -Body $ollamaRequest -ContentType "application/json" -TimeoutSec 60
    $ollamaLatency = ((Get-Date) - $ollamaStart).TotalMilliseconds
    
    Write-Host "✅ Ollama Response Received" -ForegroundColor Green
    Write-Host "Latency: $([math]::Round($ollamaLatency, 2)) ms" -ForegroundColor Yellow
    Write-Host "Response Length: $($ollamaResponse.response.Length) chars" -ForegroundColor Yellow
    Write-Host "Response Preview: $($ollamaResponse.response.Substring(0, [Math]::Min(200, $ollamaResponse.response.Length)))..." -ForegroundColor Gray
} catch {
    Write-Host "❌ Ollama Error: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

Write-Host "`n=== Testing Model Server ===`n" -ForegroundColor Cyan

# Test Model Server
$modelServerRequest = @{
    model = "tinyllama-gguf"
    prompt = $testPrompt
    stream = $false
} | ConvertTo-Json

try {
    $modelStart = Get-Date
    $modelResponse = Invoke-RestMethod -Uri $modelServerUrl -Method Post -Body $modelServerRequest -ContentType "application/json" -TimeoutSec 60
    $modelLatency = ((Get-Date) - $modelStart).TotalMilliseconds
    
    Write-Host "✅ Model Server Response Received" -ForegroundColor Green
    Write-Host "Latency: $([math]::Round($modelLatency, 2)) ms" -ForegroundColor Yellow
    $responseText = $modelResponse.runtime_response.content
    if (-not $responseText) {
        $responseText = $modelResponse.runtime_response.text
    }
    Write-Host "Response Length: $($responseText.Length) chars" -ForegroundColor Yellow
    Write-Host "Response Preview: $($responseText.Substring(0, [Math]::Min(200, $responseText.Length)))..." -ForegroundColor Gray
} catch {
    Write-Host "❌ Model Server Error: $_" -ForegroundColor Red
}

Write-Host "`n=== Comparison Complete ===`n" -ForegroundColor Cyan

