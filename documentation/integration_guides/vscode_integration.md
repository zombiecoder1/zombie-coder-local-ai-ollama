# VS Code Integration Guide

## Overview

The ZombieCoder Provider can be used as a drop-in replacement for Ollama in VS Code with the Continue extension or other AI coding assistants.

## Continue Extension Setup

### 1. Install Continue Extension

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Continue"
4. Install the Continue extension

### 2. Configure Provider Endpoint

1. Open Continue settings (Ctrl+, then search for "Continue")
2. Find the "Continue: LLM" setting
3. Set the API base URL to: `http://localhost:8007`

### 3. Model Configuration

In your `config.json` for Continue, use the following configuration:

```json
{
  "models": [
    {
      "model": "phi-2",
      "apiBase": "http://localhost:8007",
      "apiKey": "zombie-local-please-change"
    }
  ]
}
```

## Custom Instructions

You can customize the behavior by modifying the provider configuration at `config/provider_config.json`:

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

## Troubleshooting

### Model Not Loading

1. Ensure the ZombieCoderAI Windows service is running
2. Check that the model file exists in the models directory
3. Verify the model is registered in `registry/models_index.json`

### Connection Refused

1. Confirm the server is running on port 8007
2. Check Windows Firewall settings
3. Verify no other service is using port 8007

### Authentication Errors

1. If API key authentication is enabled, ensure you're providing the correct key
2. Check that the API key in `config/provider_config.json` matches what you're using

## Performance Tips

### Model Loading

- The first request to a model will take longer as it loads into memory
- Subsequent requests are much faster as the model remains resident
- Models stay loaded for 24 hours by default after last use

### Memory Management

- Monitor system memory usage when loading multiple large models
- Consider unloading unused models manually to free up memory
- Adjust `ram_threshold_mb` in the configuration if needed

## Supported Models

Currently supported models in your installation:

1. **phi-2** - 52 bytes (placeholder)
2. **phi-2-gguf** - 1.17 GB (Q2_K quantization)
3. **phi-2-gguf** - 1.25 GB (Q3_K_S quantization)
4. **qwen2.5-0.5b-instruct-gguf** - 491.40 MB
5. **qwen2.5-1.5b-instruct-gguf** - 1.12 GB
6. **deepseek-coder-1.3b** - 873.58 MB

## Advanced Configuration

### Custom Model Parameters

You can specify custom parameters for model loading by modifying the models index:

```json
{
  "models": [
    {
      "name": "qwen2.5-1.5b-instruct-gguf",
      "path": "models\\qwen2.5-1.5b-instruct-gguf\\qwen2.5-1.5b-instruct-q4_k_m.gguf",
      "size_bytes": 1117320736,
      "status": "unloaded",
      "keep_loaded": true,
      "context_length": 4096,
      "gpu_layers": "auto"
    }
  ]
}
```

### Multiple Models

You can switch between models by changing the `model` parameter in your requests:

```json
{
  "model": "qwen2.5-1.5b-instruct-gguf",
  "prompt": "Explain quantum computing in simple terms",
  "stream": false
}
```

## Logging and Debugging

Logs are stored in the `logs/` directory. Check these files if you encounter issues:

- `provider_setup_report.json` - Setup and configuration logs
- Test results from the `test/` directory

## Updates and Maintenance

To update your models or configuration:

1. Always commit your current state with git before making changes
2. Add new models to the `models/` directory
3. Run the `scripts/build_models_index.py` script to update the registry
4. Restart the ZombieCoderAI service if needed

## Support

For issues with the ZombieCoder Provider, check:

1. Documentation in the `documentation/` directory
2. Test results in the `test/` directory
3. Logs in the `logs/` directory