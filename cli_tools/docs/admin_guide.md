# ZombieCoderAI Admin Guide

## Service Installation
- NSSM installed at: C:\ProgramData\chocolatey\bin\nssm.exe
- Service name: ZombieCoderAI
- Automatic restart on failure enabled
- Service installed using: `.\scripts\install_service.bat`

## Service Management
- Start service: `nssm start ZombieCoderAI`
- Stop service: `nssm stop ZombieCoderAI`
- Check status: `nssm status ZombieCoderAI`
- Service configuration: Managed by NSSM

## Log Files
- stdout: logs\zombiecoder_stdout.log
- stderr: logs\zombiecoder_stderr.log

## Watchdog
- Watchdog script: scripts\watchdog.py
- Monitors service and restarts if needed
- Checks every 10 seconds for uvicorn processes

## Directory Structure
- models/ - Loaded models
- scripts/ - Service and model management scripts
- test/ - Test files organized in subdirectories
- test/oldtest - Old/repetitive test files
- logs/ - Service logs
- documentation/ - API specs and guides
- registry/ - Models index and metadata
- config/ - Configuration files

## API Endpoints
- List models: GET http://localhost:8007/api/tags
- Generate text: POST http://localhost:8007/api/generate
- Chat interface: POST http://localhost:8007/api/chat
- Load model: POST http://localhost:8007/runtime/load/{model}
- Unload model: POST http://localhost:8007/runtime/unload/{model}

## Troubleshooting
- If service shows "SERVICE_PAUSED" status, it's actually running
- Check logs for error details
- Restart watchdog if it stops monitoring
- Ensure port 8007 is not blocked by firewall