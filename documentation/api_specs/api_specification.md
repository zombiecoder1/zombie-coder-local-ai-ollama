# ZombieCoder Provider API Specification

## Overview

The ZombieCoder Provider API is fully compatible with the Ollama API specification, allowing seamless integration with existing tools and workflows. All endpoints follow the same request/response format as Ollama.

## Base URL

```
http://localhost:8007
```

## Authentication

API key authentication is supported but disabled by default. To enable:

1. Set `auth.enable_api_key` to `true` in `config/provider_config.json`
2. Set your preferred API key in `auth.api_key`

When enabled, include the header:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### GET /api/tags

List all available models.

**Response:**
```json
{
  "models": [
    {
      "name": "phi-2",
      "model": "phi-2",
      "modified_at": "2025-11-17T01:02:27.696947Z",
      "size": 52,
      "digest": "unknown",
      "details": {
        "format": "gguf",
        "family": "phi-2",
        "families": ["phi-2"],
        "parameter_size": "unknown",
        "quantization_level": "unknown"
      }
    }
  ]
}
```

### POST /api/generate

Generate a response from a model.

**Request:**
```json
{
  "model": "phi-2",
  "prompt": "Why is the sky blue?",
  "stream": false,
  "max_tokens": 150
}
```

**Response:**
```json
{
  "model": "phi-2",
  "created_at": "2025-11-17T01:02:27.696947Z",
  "response": "The sky appears blue due to a phenomenon called Rayleigh scattering...",
  "done": true,
  "context": [1, 2, 3, ...],
  "total_duration": 123456789,
  "load_duration": 12345678,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 12345678,
  "eval_count": 50,
  "eval_duration": 123456789
}
```

### POST /api/chat

Generate a chat response from a model.

**Request:**
```json
{
  "model": "phi-2",
  "messages": [
    {
      "role": "user",
      "content": "Why is the sky blue?"
    }
  ],
  "stream": false,
  "max_tokens": 150
}
```

**Response:**
```json
{
  "model": "phi-2",
  "created_at": "2025-11-17T01:02:27.696947Z",
  "message": {
    "role": "assistant",
    "content": "The sky appears blue due to a phenomenon called Rayleigh scattering..."
  },
  "done": true,
  "total_duration": 123456789,
  "load_duration": 12345678,
  "prompt_eval_count": 10,
  "prompt_eval_duration": 12345678,
  "eval_count": 50,
  "eval_duration": 123456789
}
```

### GET /models/installed

List all installed models with their current status.

**Response:**
```json
[
  {
    "model": "phi-2",
    "status": "ready",
    "port": 8080,
    "pid": 15104,
    "updated_at": "2025-11-17T01:02:27.696947Z"
  }
]
```

### POST /runtime/load/{model}

Force load a model into memory.

**Response:**
```json
{
  "status": "ready",
  "model": "phi-2",
  "port": 8080,
  "pid": 15104,
  "command": "C:\\model\\config\\llama.cpp\\server.exe -m C:\\model\\models\\phi-2\\phi-2.Q4_K_M.gguf -p 8080 -t 4"
}
```

### POST /runtime/unload/{model}

Force unload a model from memory.

**Response:**
```json
{
  "status": "unloaded",
  "model": "phi-2"
}
```

## Model Management

### Lazy Loading

Models are automatically loaded on first request if not already loaded. Subsequent requests use the already-loaded instance.

### Persistent Residency

Once loaded, models remain in memory in a "sleep" state unless:
1. Explicitly unloaded via `/runtime/unload/{model}`
2. System experiences memory pressure (configurable threshold)
3. Manual administrative action

### Configuration

Models are configured with the following defaults:
- `keep_loaded`: true (models remain resident)
- `idle_unload_seconds`: 86400 (24 hours)
- `gpu_layers`: "auto"
- `context_length`: 4096

## Error Handling

All API responses follow standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (when API key authentication is enabled)
- `404` - Not Found (model not found)
- `500` - Internal Server Error

Error responses include a JSON body with error details:
```json
{
  "error": "Model not found"
}
```

## Streaming Responses

All generate and chat endpoints support streaming responses by setting `stream: true` in the request. Streamed responses follow the same format as Ollama with server-sent events.

## Rate Limiting

No rate limiting is implemented by default, but can be added through reverse proxy configuration if needed.

## CORS

CORS is enabled for all origins by default to support browser-based applications.