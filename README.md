# 🧟 ZombieCoder Local AI Framework

**যেখানে কোড ও কথা বলে** | A lightweight local AI framework for running language models locally

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](./test)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## ✨ Features

### 🚀 Core Capabilities
- **Local AI Models** - Run GGUF format models (TinyLlama, Phi-2, etc.)
- **REST API** - FastAPI-based server with comprehensive endpoints
- **Session Management** - Track conversation context across requests
- **Model Lifecycle** - Lazy loading, auto-unload, idle detection
- **Download Manager** - Direct HuggingFace Hub integration
- **Runtime Orchestrator** - llama.cpp backend with process management

### 🎯 Key Benefits
- ✅ **100% Local** - No cloud dependencies, complete privacy
- ✅ **Lightweight** - ~15MB framework, models load on-demand
- ✅ **Fast** - 14+ tokens/sec on CPU, faster with GPU
- ✅ **Easy Setup** - Python + llama.cpp, minimal dependencies
- ✅ **Production Ready** - Full test suite (100% passing), error handling, logging

---

## 🖥️ System Requirements

### Minimum
- **OS:** Windows 10/11, Linux, macOS
- **RAM:** 8 GB (16 GB recommended)
- **Storage:** 10 GB free space
- **Python:** 3.8 or higher

### Recommended
- **RAM:** 16 GB+
- **GPU:** CUDA-compatible (optional, for 10x+ speed)
- **Storage:** 20 GB+ (for multiple models)

---

## 📦 Installation

### 1. Clone Repository
```bash
git clone https://github.com/zombiecoder1/zombie-coder-local-ai-ollama.git
cd zombie-coder-local-ai-ollama
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Download llama.cpp Runtime
Download llama.cpp from [official releases](https://github.com/ggerganov/llama.cpp/releases)

Place binary in:
```
C:\model\config\llama.cpp\server.exe  (Windows)
~/model/config/llama.cpp/server       (Linux/Mac)
```

### 4. Start Server
```bash
python model_server.py
```

Server starts at: **http://localhost:8155**


---

## 🚀 Quick Start

### Download a Model
```bash
curl -X POST http://localhost:8155/download/start \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "tinyllama-gguf",
    "repo_id": "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
  }'

# Check progress
curl http://localhost:8155/download/status/tinyllama-gguf
```

### Load & Use Model
```bash
# Load model
curl -X POST http://localhost:8155/runtime/load/tinyllama-gguf?threads=4

# Generate text
curl -X POST http://localhost:8155/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tinyllama-gguf",
    "prompt": "Write a Python hello world program"
  }'

# Unload model
curl -X POST http://localhost:8155/runtime/unload/tinyllama-gguf
```

---

## 📚 Documentation

Detailed documentation available in [`doc/`](./doc/) folder:

- **[API Documentation](./doc/README.md)** - Complete API reference
- **[System Integration](./doc/SYSTEMS_INTEGRATION.md)** - Integration guide
- **[Current Capabilities](./doc/CURRENT_CAPABILITIES.md)** - Features & limitations
- **[Verification Report](./doc/VERIFICATION_COMPLETE.md)** - Test results

---

## 🧪 Testing

### Run All Tests
```bash
cd test
python run_core_tests.py
```

### Test Results
✅ **5/5 Core Tests Passing (100%)**

- `01_preflight_check.py` - System health check
- `02_model_lifecycle.py` - Model operations
- `03_api_standard_check.py` - API compatibility
- `04_ui_data_integrity.py` - Data validation
- `05_integrated_session_test.py` - Session management

**Test Coverage:** See [`test/README.md`](./test/README.md)

---

## 📊 API Endpoints

### System Info
```bash
GET  /health              # Server health
GET  /system/info         # Hardware detection
GET  /models/installed    # List local models
GET  /models/available    # Recommended models
```

### Runtime Control
```bash
GET  /runtime/status           # Current state
POST /runtime/load/{model}     # Load model
POST /runtime/unload/{model}   # Unload model
GET  /runtime/config           # Configuration
```

### Text Generation
```bash
POST /api/generate             # Generate text
GET  /api/tags                 # List models
```

### Session Management
```bash
POST /api/session/start              # Create session
GET  /api/session/status/{id}        # Check session
POST /api/session/end/{id}           # End session
```

### Download Manager
```bash
POST /download/start                 # Start download
GET  /download/status/{model}        # Check progress
POST /download/cancel/{model}        # Cancel download
```

Full API docs: [`doc/README.md`](./doc/README.md)

---

## 📈 Performance

### Benchmarks (TinyLlama 1.1B, Q2_K)

| Metric | CPU (4 cores) | GPU (CUDA) |
|--------|---------------|------------|
| Load Time | 3-4 seconds | 2-3 seconds |
| Tokens/sec | 14 tokens/s | 150+ tokens/s |
| Memory Usage | 2-3 GB | 1-2 GB |
| First Token | ~60ms | ~20ms |

**Tested on:** Intel i5-4590, 16GB RAM, Windows 10

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│      FastAPI Server (Port 8155)         │
├─────────────────────────────────────────┤
│  ┌────────┐  ┌────────┐  ┌──────────┐ │
│  │ Models │  │Download│  │ Session  │ │
│  │ API    │  │Manager │  │ Manager  │ │
│  └────────┘  └────────┘  └──────────┘ │
├─────────────────────────────────────────┤
│        Runtime Orchestrator             │
│  (Model Loading, Process Management)    │
├─────────────────────────────────────────┤
│      llama.cpp Server (Dynamic)         │
│           (Port 8080+)                  │
└─────────────────────────────────────────┘
```

---

## 💻 Usage Examples

### Python Client
```python
import requests

# Load model
requests.post(
    "http://localhost:8155/runtime/load/tinyllama-gguf",
    params={"threads": 4}
)

# Generate text
response = requests.post(
    "http://localhost:8155/api/generate",
    json={
        "model": "tinyllama-gguf",
        "prompt": "Explain quantum computing"
    }
)

print(response.json()['runtime_response']['content'])
```

### JavaScript Client
```javascript
// Generate text
const response = await fetch('http://localhost:8155/api/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'tinyllama-gguf',
    prompt: 'What is AI?'
  })
});

const data = await response.json();
console.log(data.runtime_response.content);
```

More examples: [`examples/`](./examples/)

---

## 🔧 Configuration

### Environment Variables
```bash
MODEL_SERVER_PORT=8155          # API server port
MODELS_DIR=/path/to/models      # Models directory
HUGGINGFACE_HUB_TOKEN=token     # HF token (optional)
```

### Recommended Models

| System RAM | Model | Quantization | Speed |
|------------|-------|--------------|-------|
| 8 GB | TinyLlama 1.1B | Q2_K | 10-15 t/s |
| 16 GB | Phi-2 2.7B | Q4_K_M | 8-12 t/s |
| 32 GB | Llama-2 7B | Q5_K_M | 5-10 t/s |

---

## 🛠️ Troubleshooting

### Model Not Loading
```bash
# Check runtime config
curl http://localhost:8155/runtime/config

# Verify model exists
curl http://localhost:8155/models/installed
```

### Slow Performance
- Use quantized models (Q2_K, Q4_K)
- Increase thread count: `?threads=8`
- Enable GPU acceleration (if available)

### Out of Memory
- Use smaller quantization (Q2_K instead of Q8_0)
- Use smaller model (TinyLlama vs Phi-2)
- Close other applications

---

## 📁 Project Structure

```
C:\model/
├── doc/                    # 📚 Documentation
│   ├── README.md          # API reference
│   ├── SYSTEMS_INTEGRATION.md
│   ├── CURRENT_CAPABILITIES.md
│   └── VERIFICATION_COMPLETE.md
├── test/                   # 🧪 Test suite
│   ├── 01_preflight_check.py
│   ├── 02_model_lifecycle.py
│   ├── 03_api_standard_check.py
│   ├── 04_ui_data_integrity.py
│   ├── 05_integrated_session_test.py
│   ├── run_core_tests.py
│   └── README.md
├── static/                 # 🌐 Web UI
├── models/                 # 🤖 Downloaded models
├── logs/                   # 📝 Server logs
├── data/                   # 💾 Database
├── model_server.py        # 🚀 Main server
├── router.py              # 🔄 Runtime orchestrator
├── downloader.py          # ⬇️ Download manager
├── db_manager.py          # 💾 Model registry
├── system_detector.py     # 🖥️ Hardware detection
└── requirements.txt       # 📦 Dependencies
```

---

## 🤝 Contributing

Contributions welcome! See [`CONTRIBUTING.md`](./CONTRIBUTING.md)

### Development Setup
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
cd test && python run_all_tests.py
```

---

## 📄 License

MIT License - see [`LICENSE`](./LICENSE)

---

## 👥 Credits

**Created by:** Sahon Srabon  
**Organization:** Developer Zone  
**Website:** https://zombiecoder.my.id/  
**Contact:** infi@zombiecoder.my.id

### Technologies
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - Inference engine
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [HuggingFace Hub](https://huggingface.co/) - Model repository

---

## 📞 Support

- **GitHub Issues:** [Report issues](https://github.com/zombiecoder1/zombie-coder-local-ai-ollama/issues)
- **Email:** infi@zombiecoder.my.id
- **Phone:** +880 1323-626282

---

## 🎯 Quick Links

- 📚 [Full Documentation](./doc/)
- 🧪 [Test Suite](./test/)
- 🌐 [Web UI](http://localhost:8155)
- 📊 [API Reference](./doc/README.md)
- ✅ [Test Results](./doc/VERIFICATION_COMPLETE.md)

---

**Made with ❤️ by ZombieCoder**  
*Building AI tools that respect privacy and run anywhere*

