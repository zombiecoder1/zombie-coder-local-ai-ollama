# ZombieCoder Provider Ecosystem Overview

## System Architecture

The ZombieCoder Provider Ecosystem is designed to be a robust, persistent AI model serving platform that can act as a primary provider or fallback to Ollama. The system is built with the following core principles:

### 1. Ollama Compatibility
- Supports all Ollama API endpoints for seamless integration
- Can be used as a drop-in replacement for existing Ollama-based projects
- Maintains compatibility with VS Code, Cursor, Zed, and other AI-enabled tools

### 2. Persistent Model Management
- Models remain loaded in memory (sleep/idle mode) after first load
- Automatic lazy loading on first request
- Configurable keep-loaded behavior (default: true)
- Idle timeout set to 24 hours by default

### 3. Robust Process Management
- Runs as a Windows service to prevent accidental termination
- Watchdog process monitors and restarts the server if needed
- Recovery settings ensure automatic restart on failure

## Directory Structure

```
C:\model\
├── config\                 # Configuration files
├── documentation\          # API specs and documentation
├── logs\                  # Runtime logs and test results
├── models\                 # GGUF model files
├── registry\               # Models index and metadata
├── scripts\                # Utility scripts
├── test\                   # Test files and cases
└── model_server.py         # Main server application
```

## Core Components

### 1. Model Server
The main server application that exposes Ollama-compatible endpoints and manages model lifecycle.

### 2. Models Index
A JSON registry at `registry/models_index.json` that tracks all available models with their metadata.

### 3. Windows Service
The server runs as a Windows service named "ZombieCoderAI" for persistent operation.

### 4. Watchdog
A separate Python process that monitors the server and restarts it if it stops unexpectedly.

## API Endpoints

### Ollama-Compatible Endpoints
- `GET /api/tags` - List all available models
- `POST /api/generate` - Generate text completions
- `POST /api/chat` - Chat-based interactions
- `GET /models/installed` - List installed models
- `POST /runtime/load/{model}` - Force load a model
- `POST /runtime/unload/{model}` - Force unload a model

### Model Management
- Automatic loading on first request
- Persistent residency in memory
- Configurable unload policies

## Configuration

### Provider Config (`config/provider_config.json`)
```json
{
  "server_port": 8007,
  "models_dir": "C:\\model\\models",
  "keep_loaded_default": true,
  "idle_unload_seconds": 86400,
  "ram_threshold_mb": 14000,
  "upstream_ollama": null,
  "auth": {
    "enable_api_key": true,
    "api_key": "zombie-local-please-change"
  }
}
```

## Integration Guides

### VS Code Integration
Use the standard Ollama configuration but point to `http://localhost:8007` instead of the default Ollama port.

### Cursor AI Integration
Configure the provider endpoint to `http://localhost:8007` in Cursor settings.

### Zed AI Integration
Set the Ollama URL to `http://localhost:8007` in Zed configuration.

### CLI Tools
All existing CLI tools that work with Ollama will work with the ZombieCoder Provider by simply changing the endpoint URL.

## Development Workflow

### Git Practices
- Always commit changes before making modifications
- Use descriptive commit messages
- Maintain a clean git history for easy rollback

### Testing
- Place all test files in the `test/` directory
- Run tests before deploying changes
- Log test results in `logs/` directory

### Documentation
- Keep API specifications up to date
- Document integration guides
- Maintain changelog of changes