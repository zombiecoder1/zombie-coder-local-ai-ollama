# ZombieCoder Local AI - Server Starter
# Usage: .\start_server.ps1

Write-Host "🚀 ZombieCoder Local AI সার্ভার চালু হচ্ছে..." -ForegroundColor Cyan

# পুরাতন Python প্রসেস বন্ধ করা
Write-Host "পুরাতন প্রসেস চেক করা হচ্ছে..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*Python*" } | ForEach-Object {
    Write-Host "  → Python প্রসেস বন্ধ করা হচ্ছে (PID: $($_.Id))" -ForegroundColor Gray
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 2

# সার্ভার চালু করা
Write-Host "`n✅ সার্ভার চালু হচ্ছে পোর্ট 8155-এ..." -ForegroundColor Green
Write-Host "   URL: http://127.0.0.1:8155/" -ForegroundColor Cyan
Write-Host "   UI:  http://127.0.0.1:8155/static/allindex.html" -ForegroundColor Cyan
Write-Host "`n⏹️  বন্ধ করতে Ctrl+C চাপুন`n" -ForegroundColor Yellow

cd $PSScriptRoot
$env:PYTHONUNBUFFERED = 1
python -m uvicorn model_server:app --host 0.0.0.0 --port 8155 --log-level info
