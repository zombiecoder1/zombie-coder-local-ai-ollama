# Test if Model Server responds like Ollama

$testPrompt = "Hello"
$modelName = "tinyllama-gguf"

Write-Host "`n=== Testing Model Server Ollama Compatibility ===`n" -ForegroundColor Cyan

# Test 1: /api/generate endpoint (Ollama style)
Write-Host "Test 1: /api/generate endpoint" -ForegroundColor Yellow
$request1 = @{
    model = $modelName
    prompt = $testPrompt
    stream = $false
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "http://localhost:8155/api/generate" -Method Post -Body $request1 -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ Response received" -ForegroundColor Green
    Write-Host "Model: $($response1.model)" -ForegroundColor Gray
    Write-Host "Latency: $($response1.latency_ms) ms" -ForegroundColor Gray
    if ($response1.runtime_response.content) {
        Write-Host "Content: $($response1.runtime_response.content.Substring(0, [Math]::Min(100, $response1.runtime_response.content.Length)))" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Test 2: /api/chat endpoint
Write-Host "`nTest 2: /api/chat endpoint" -ForegroundColor Yellow
$request2 = @{
    model = $modelName
    messages = @(@{
        role = "user"
        content = $testPrompt
    })
    stream = $false
} | ConvertTo-Json -Depth 5

try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:8155/api/chat" -Method Post -Body $request2 -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ Response received" -ForegroundColor Green
    if ($response2.runtime_response.content) {
        Write-Host "Content: $($response2.runtime_response.content.Substring(0, [Math]::Min(100, $response2.runtime_response.content.Length)))" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===`n" -ForegroundColor Cyan

