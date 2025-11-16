@echo off
:: Batch file to run the PowerShell service installation script with administrator privileges

echo Installing ZombieCoderAI Service...
echo ==================================

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator
    powershell -ExecutionPolicy Bypass -File "%~dp0install_service.ps1"
) else (
    echo Requesting Administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d \"%cd%\" && \"%~dp0install_service.bat\"' -Verb RunAs"
)

echo.
echo Press any key to exit...
pause >nul