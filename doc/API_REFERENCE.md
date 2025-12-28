# 📚 ZombieCoder Local AI - API Reference

Complete API documentation for all endpoints.

**Base URL:** `http://localhost:8155`

---

## 🔍 Table of Contents

1. [Health & System](#health--system)
2. [Models Management](#models-management)
3. [Runtime Control](#runtime-control)
4. [Text Generation](#text-generation)
5. [Session Management](#session-management)
6. [Download Manager](#download-manager)
7. [Monitoring](#monitoring)
8. [Authentication](#authentication)

---

## 🏥 Health & System

### GET /health
Server health check

**Response:**
```json
{
  "status": "healthy",
  "service": "ZombieCoder Local AI Framework",
  "version": "0.1.0",
  "models_dir": "C:\\model\\models",
  "port": 8155,
  "timestamp": "2025-10-18T00:00:00",
  "uptime_sec": 123
}
```

### GET /system/info
Hardware and system information

**Response:**
```json
{
  "total_ram_gb": 15.87,
  "cpu_model": "Intel64 Family 6 Model 60",
  "gpu_info": "Intel HD Graphics 4400",
  "tier": "good",
  "os": "Windows 10"
}
```

**Tier Values:**
- `entry_level` - 8GB RAM
- `good` - 16GB RAM
- `high_end` - 32GB+ RAM

---

## 🤖 Models Management

### GET /models/installed
List all installed models

**Response:**
```json
{
  "models": [
    {
      "name": "deepseek-coder-1.3b",
      "path": "C:\\model\\models\\deepseek-coder-1.3b",
      "size_mb": 8076.8,
      "detected_at": "2025-10-18T00:00:00"
    }
  ],
  "count": 1,
  "total_size_mb": 8076.8
}
```

### GET /models/available
Get recommended models based on system tier

**Response:**
```json
[
  {
    "name": "TinyLlama-1.1B",
    "size": "1.1B",
    "ram_required": "2-3 GB",
    "description": "সবচেয়ে হালকা, সাধারণ টেক্সট ও চ্যাট",
    "huggingface_id": "TheBloke/TinyLlama-1.1B-Chat-GGUF",
    "recommended": true,
    "compatibility": "recommended"
  }
]
```

### GET /api/tags
List models in standard format

**Response:**
```json
{
  "models": [
    {
      "name": "deepseek-coder-1.3b",
      "model": "deepseek-coder-1.3b",
      "modified_at": "2025-10-18T00:00:00",
      "size": 8469158021,
      "digest": "local",
      "status": "installed",
      "runtime_status": "stopped",
      "format": "gguf",
      "quantization": "Q2_K",
      "details": {
        "format": "gguf",
        "family": "llama",
        "parameter_size": "1.1B",
        "quantization_level": "Q2_K"
      }
    }
  ]
}
```

---

## ⚙️ Runtime Control

### GET /runtime/status
Current runtime state

**Response:**
```json
{
  "models": [
    {
      "model": "deepseek-coder-1.3b",
      "status": "ready",
      "port": 8080,
      "pid": 12345,
      "last_access_ts": 1760726329.207
    }
  ],
  "persisted": []
}
```

**Status Values:**
- `ready` - Model loaded and ready
- `loading` - Currently loading
- `stopped` - Not running

### POST /runtime/load/{model}
Load a model into memory

**Parameters:**
- `threads` (query, optional) - Number of CPU threads (default: 4)

**Request:**
```bash
POST /runtime/load/deepseek-coder-1.3b?threads=4
```

**Response:**
```json
{
  "status": "ready",
  "model": "deepseek-coder-1.3b",
  "port": 8080,
  "pid": 12345,
  "command": "C:\\model\\config\\llama.cpp\\server.exe --model ...",
  "log": "C:\\model\\logs\\runtime_deepseek-coder-1.3b.log",
  "gpu_layers": 0
}
```

### POST /runtime/unload/{model}
Unload a model from memory

**Request:**
```bash
POST /runtime/unload/deepseek-coder-1.3b
```

**Response:**
```json
{
  "status": "stopped",
  "model": "deepseek-coder-1.3b"
}
```

### GET /runtime/config
Runtime configuration check

**Response:**
```json
{
  "exists": true,
  "path": "C:\\model\\config\\llama.cpp\\server.exe",
  "message": null
}
```

---

## 💬 Text Generation

### POST /api/generate
Generate text using loaded model

**Request Body:**
```json
{
  "model": "deepseek-coder-1.3b",
  "prompt": "Write a Python hello world program",
  "stream": false,
  "options": {
    "session_id": "optional-session-id"
  }
}
```

**Response:**
```json
{
  "model": "deepseek-coder-1.3b",
  "runtime_port": 8080,
  "runtime_response": {
    "content": "print('Hello, World!')",
    "tokens_predicted": 10,
    "tokens_evaluated": 5,
    "timings": {
      "prompt_ms": 50,
      "predicted_ms": 200,
      "predicted_per_second": 50
    }
  }
}
```

**Error Responses:**
- `404` - Model not found
- `409` - Model not loaded (need to load first)
- `502` - Runtime error

---

## 🔐 Session Management

### POST /api/session/start
Create a new session

**Request Body:**
```json
{
  "session_id": "optional-custom-id"
}
```

**Response:**
```json
{
  "session_id": "sess-1760726404",
  "status": "active"
}
```

### GET /api/session/status/{session_id}
Get session information

**Response:**
```json
{
  "session": {
    "session_id": "sess-1760726404",
    "created_at": "2025-10-18T00:00:00",
    "last_seen_at": "2025-10-18T00:05:00",
    "last_model": "deepseek-coder-1.3b"
  },
  "status": "active"
}
```

### POST /api/session/end/{session_id}
End a session

**Response:**
```json
{
  "session_id": "sess-1760726404",
  "status": "ended"
}
```

---

## ⬇️ Download Manager

### POST /download/start
Start model download from HuggingFace

**Request Body:**
```json
{
  "model_name": "deepseek-coder-1.3b",
  "repo_id": "TheBloke/TinyLlama-1.1B-Chat-GGUF",
  "revision": "main"
}
```

**Response:**
```json
{
  "status": "started",
  "model_name": "deepseek-coder-1.3b",
  "repo_id": "TheBloke/TinyLlama-1.1B-Chat-GGUF"
}
```

### GET /download/status/{model}
Check download progress

**Response:**
```json
{
  "status": "downloading",
  "job": {
    "repo_id": "TheBloke/TinyLlama-1.1B-Chat-GGUF",
    "target_dir": "C:\\model\\models\\deepseek-coder-1.3b",
    "started_at": "2025-10-18T00:00:00",
    "progress": 45.5,
    "state": "downloading"
  }
}
```

**State Values:**
- `downloading` - In progress
- `done` - Completed
- `error` - Failed
- `cancelled` - User cancelled

### POST /download/cancel/{model}
Cancel ongoing download

**Response:**
```json
{
  "status": "cancelled",
  "model": "deepseek-coder-1.3b"
}
```

---

## 📊 Monitoring

### GET /monitoring/summary
System and runtime summary

**Response:**
```json
{
  "uptime_sec": 3600,
  "system": {
    "total_ram_gb": 15.87,
    "tier": "good"
  },
  "models_indexed": 3,
  "runtime": {
    "models": []
  }
}
```

### GET /performance/snapshot
Real-time performance metrics

**Response:**
```json
{
  "cpu_percent": 25.5,
  "memory": {
    "total_gb": 15.87,
    "used_gb": 8.5,
    "percent": 53.5
  },
  "disk": {
    "total_gb": 500,
    "used_gb": 250,
    "percent": 50
  },
  "network": {
    "bytes_sent": 1024000,
    "bytes_recv": 2048000
  },
  "process": {
    "rss_mb": 150.5,
    "threads": 8,
    "open_files": 15
  },
  "timestamp": "2025-10-18T00:00:00"
}
```

### GET /logs/recent
Recent API requests

**Response:**
```json
{
  "events": [
    {
      "ts": "2025-10-18T00:00:00",
      "method": "POST",
      "path": "/api/generate",
      "status": 200,
      "duration_ms": 4500
    }
  ]
}
```

### GET /logs/server
Server log file (last N lines)

**Parameters:**
- `limit` (query, optional) - Number of lines (default: 200)

**Response:**
```json
{
  "path": "C:\\model\\logs\\server.log",
  "tail": [
    "2025-10-18T00:00:00\tPOST\t/api/generate\t200\t4500ms",
    "..."
  ]
}
```

### GET /provider/about
Provider information

**Response:**
```json
{
  "product": "ZombieCoder Local AI",
  "tagline": "যেখানে কোড ও কথা বলে",
  "owner": "Sahon Srabon",
  "company": "Developer Zone",
  "contact": "+880 1323-626282",
  "website": "https://zombiecoder.my.id/",
  "email": "infi@zombiecoder.my.id"
}
```

---

## 🔑 Authentication

### POST /auth/hf_token
Set HuggingFace token for private models

**Request Body:**
```json
{
  "token": "hf_xxxxxxxxxxxxxxxxxxxxx"
}
```

**Response:**
```json
{
  "ok": true,
  "token_set": true
}
```

### GET /auth/status
Check if token is set

**Response:**
```json
{
  "token_set": true
}
```

---

## 📝 Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 404 | Not Found | Model/endpoint not found |
| 409 | Conflict | Model not loaded |
| 422 | Validation Error | Invalid request data |
| 502 | Bad Gateway | Runtime error |
| 503 | Service Unavailable | Model loading |

---

## 🔄 Request Flow

### Typical Workflow:

1. **Check Health:**
   ```bash
   GET /health
   ```

2. **List Models:**
   ```bash
   GET /models/installed
   ```

3. **Load Model:**
   ```bash
   POST /runtime/load/deepseek-coder-1.3b?threads=4
   ```

4. **Wait for Ready:**
   ```bash
   GET /runtime/status
   # Check status == "ready"
   ```

5. **Generate Text:**
   ```bash
   POST /api/generate
   {
     "model": "deepseek-coder-1.3b",
     "prompt": "Your prompt here"
   }
   ```

6. **Unload When Done:**
   ```bash
   POST /runtime/unload/deepseek-coder-1.3b
   ```

---

## 🐍 Python Example

```python
import requests
import time

BASE_URL = "http://localhost:8155"

# 1. Load model
response = requests.post(
    f"{BASE_URL}/runtime/load/deepseek-coder-1.3b",
    params={"threads": 4}
)
print(f"Model loaded: {response.json()['status']}")

# 2. Wait for ready
time.sleep(3)

# 3. Generate
response = requests.post(
    f"{BASE_URL}/api/generate",
    json={
        "model": "deepseek-coder-1.3b",
        "prompt": "Write Python factorial function"
    }
)

result = response.json()
print(f"Response: {result['runtime_response']['content']}")

# 4. Unload
requests.post(f"{BASE_URL}/runtime/unload/deepseek-coder-1.3b")
```

---

## 🌐 JavaScript Example

```javascript
const BASE_URL = 'http://localhost:8155';

// Load model
await fetch(`${BASE_URL}/runtime/load/deepseek-coder-1.3b?threads=4`, {
  method: 'POST'
});

// Wait for ready
await new Promise(r => setTimeout(r, 3000));

// Generate
const response = await fetch(`${BASE_URL}/api/generate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'deepseek-coder-1.3b',
    prompt: 'Write JavaScript hello world'
  })
});

const data = await response.json();
console.log(data.runtime_response.content);

// Unload
await fetch(`${BASE_URL}/runtime/unload/deepseek-coder-1.3b`, {
  method: 'POST'
});
```

---

## 📞 Support

For API issues or questions:
- **Email:** infi@zombiecoder.my.id
- **GitHub:** https://github.com/zombiecoder1/zombie-coder-local-ai-ollama/issues

---

**Last Updated:** 2025-10-18  
**API Version:** 0.1.0

