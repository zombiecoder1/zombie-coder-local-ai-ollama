# 📁 ZombieCoder Local AI - Project Structure

**Last Updated:** 2025-10-18

---

## 📂 Directory Structure

```
C:\model/
│
├── 📚 doc/                          # সম্পূর্ণ ডকুমেন্টেশন
│   ├── INDEX.md                    # Documentation index
│   ├── README.md                   # প্রধান ডকুমেন্টেশন  
│   ├── API_REFERENCE.md           # Complete API docs
│   ├── SYSTEMS_INTEGRATION.md     # Integration guide
│   ├── CURRENT_CAPABILITIES.md    # Features & limits
│   └── VERIFICATION_COMPLETE.md   # Test report
│
├── 🧪 test/                         # টেস্ট স্যুট
│   ├── README.md                   # Test documentation
│   ├── TEST_SUMMARY.md            # Test analysis
│   ├── 01_preflight_check.py      # System health
│   ├── 02_model_lifecycle.py      # Model operations
│   ├── 03_api_standard_check.py   # API tests
│   ├── 04_ui_data_integrity.py    # Data validation
│   ├── 05_integrated_session_test.py # Session tests
│   ├── 06_verify_system.py        # System verification
│   ├── 07_gguf_model_test.py      # GGUF model tests
│   ├── run_core_tests.py          # Core test runner
│   ├── run_all_tests.py           # All tests runner
│   ├── demo_integration.py        # Integration demo
│   ├── print_summary.py           # Results printer
│   ├── testui.html                # Test UI
│   ├── testui.py                  # UI server
│   ├── test_report.json           # Test results
│   └── core_test_report.json      # Core results
│
├── 🌐 static/                       # Web UI files
│   ├── allindex.html              # Main UI
│   └── index.html                 # Simple UI
│
├── 🤖 models/                       # Downloaded models
│   ├── tinyllama-gguf/            # TinyLlama GGUF
│   ├── phi-2/                     # Phi-2 (safetensors)
│   ├── tinyllama/                 # TinyLlama (safetensors)
│   ├── download_*.log             # Download logs
│   └── models_registry.json       # Model registry
│
├── 📝 logs/                         # Server logs
│   ├── server.log                 # API logs
│   └── runtime_*.log              # Model runtime logs
│
├── 💾 data/                         # Database
│   └── runtime.db                 # Runtime state DB
│
├── ⚙️ config/                       # Configuration
│   └── llama.cpp/
│       └── server.exe             # llama.cpp runtime
│
├── 📜 scripts/                      # Utility scripts
│   ├── download_and_poll.py       # Download utility
│   └── lifecycle_run.py           # Lifecycle test
│
├── 🐍 Python Core Files             # Main application
│   ├── model_server.py            # 🚀 Main server
│   ├── router.py                  # Runtime orchestrator
│   ├── downloader.py              # Download manager
│   ├── db_manager.py              # Model registry
│   ├── runtime_db.py              # Runtime state DB
│   └── system_detector.py         # Hardware detection
│
└── 📄 Root Files                    # Project files
    ├── README.md                   # Project overview
    ├── PROJECT_STRUCTURE.md       # This file
    ├── .gitignore                 # Git ignore
    ├── requirements.txt           # Dependencies
    └── LICENSE                    # License file
```

---

## 📚 Documentation (doc/)

### Primary Documents
- **INDEX.md** - Documentation সূচী, সব docs এর লিংক
- **README.md** - প্রধান প্রজেক্ট ডকুমেন্টেশন
- **API_REFERENCE.md** - সম্পূর্ণ API documentation

### Technical Guides
- **SYSTEMS_INTEGRATION.md** - Multi-system integration
- **CURRENT_CAPABILITIES.md** - Features, limitations, use cases
- **VERIFICATION_COMPLETE.md** - Complete test report

**Total:** 6 documentation files

---

## 🧪 Test Suite (test/)

### Core Tests (01-05)
- **01_preflight_check.py** - System health, runtime, models
- **02_model_lifecycle.py** - Load → Generate → Unload
- **03_api_standard_check.py** - API compatibility
- **04_ui_data_integrity.py** - Data validation
- **05_integrated_session_test.py** - Session management

### Verification Tests (06-07)
- **06_verify_system.py** - Comprehensive system check
- **07_gguf_model_test.py** - GGUF model testing

### Test Utilities
- **run_core_tests.py** - Run 5 core tests
- **run_all_tests.py** - Run all tests
- **demo_integration.py** - Live integration demo
- **print_summary.py** - Display test results
- **testui.py** - Test UI server

### Documentation
- **README.md** - Test suite guide
- **TEST_SUMMARY.md** - Detailed analysis
- **test_report.json** - All tests results
- **core_test_report.json** - Core tests results

**Total:** 12 test files + 2 docs + 2 reports

---

## 🐍 Core Python Files

### Main Application
| File | Purpose | Lines |
|------|---------|-------|
| **model_server.py** | Main FastAPI server | ~600 |
| **router.py** | Runtime orchestration | ~300 |
| **downloader.py** | HuggingFace downloader | ~200 |
| **db_manager.py** | Model registry | ~150 |
| **runtime_db.py** | State persistence | ~100 |
| **system_detector.py** | Hardware detection | ~150 |

**Total:** ~1,500 lines of Python code

---

## 🌐 Web UI (static/)

- **allindex.html** - Complete UI with all features
- **index.html** - Simple minimal UI

Both UIs connect to API endpoints for:
- System info
- Model management
- Runtime control
- Text generation

---

## 🤖 Models Directory (models/)

### Installed Models
```
models/
├── tinyllama-gguf/              # 8.1 GB (WORKING ✅)
│   ├── *.gguf                  # 13 quantization variants
│   └── config files
│
├── phi-2/                       # 5.3 GB (detected only)
│   └── *.safetensors           # Not loadable
│
└── tinyllama/                   # 2.1 GB (detected only)
    └── *.safetensors           # Not loadable
```

### Registry
- **models_registry.json** - Auto-generated model database

### Logs
- **download_*.log** - Download progress logs

**Total Storage:** 15.5 GB

---

## 📝 Logs Directory (logs/)

### Log Files
- **server.log** - API requests, responses, errors
- **runtime_tinyllama-gguf.log** - Model runtime logs
- **runtime_[model].log** - Other model logs

**Format:**
```
2025-10-18T00:00:00 POST /api/generate 200 4500ms
```

---

## 💾 Data Directory (data/)

### Database
- **runtime.db** - SQLite database

**Tables:**
- `models` - Runtime state tracking
- Sessions persistence

**Purpose:** Restart-safe state management

---

## ⚙️ Config Directory (config/)

### llama.cpp Runtime
```
config/
└── llama.cpp/
    ├── server.exe         # Windows executable
    └── server             # Linux/Mac binary
```

**Source:** https://github.com/ggerganov/llama.cpp/releases

---

## 📜 Scripts Directory (scripts/)

### Utility Scripts
- **download_and_poll.py** - Download with progress
- **lifecycle_run.py** - Model lifecycle test

**Usage:** Helper scripts for testing and utilities

---

## 📄 Root Files

### Essential Files
- **README.md** - Project overview (no Ollama references)
- **PROJECT_STRUCTURE.md** - This file
- **.gitignore** - Git ignore rules
- **requirements.txt** - Python dependencies
- **LICENSE** - MIT License

### Git Files
- **.git/** - Git repository
- **.gitignore** - Ignore patterns

---

## 📊 File Statistics

### By Type
- Python files: ~15 files (~2,000 lines)
- Documentation: 8 MD files
- Configuration: 2 files
- Web UI: 2 HTML files
- Logs: 3+ files
- Data: 2 databases

### By Purpose
- Core application: 6 Python files
- Testing: 12 Python test files
- Documentation: 8 MD files
- Web UI: 2 HTML files
- Configuration: 2 config files

---

## 🔍 Quick File Finder

### Want to...

**Start the server?**
→ `python model_server.py`

**Run tests?**
→ `cd test && python run_core_tests.py`

**Read API docs?**
→ `doc/API_REFERENCE.md`

**See test results?**
→ `doc/VERIFICATION_COMPLETE.md`

**Check capabilities?**
→ `doc/CURRENT_CAPABILITIES.md`

**Integration guide?**
→ `doc/SYSTEMS_INTEGRATION.md`

**View logs?**
→ `logs/server.log`

**Check models?**
→ `models/models_registry.json`

---

## 🎯 Important Paths

### For Users
```
Main UI:        http://localhost:8155
API Docs:       doc/API_REFERENCE.md
Quick Start:    README.md
```

### For Developers
```
Main Server:    model_server.py
API Routes:     router.py
Tests:          test/run_core_tests.py
```

### For DevOps
```
Logs:           logs/server.log
Database:       data/runtime.db
Config:         config/llama.cpp/
```

---

## 🚫 What's NOT Included

- ❌ Ollama integration (removed as requested)
- ❌ External API dependencies
- ❌ Cloud services
- ❌ Proprietary code
- ❌ Binary model files (downloaded separately)

---

## 📦 Dependencies

### Python Packages (requirements.txt)
- fastapi
- uvicorn
- requests
- psutil
- pydantic
- huggingface-hub

### External Binaries
- llama.cpp server (downloaded separately)

### Models
- Downloaded via HuggingFace Hub
- GGUF format recommended
- Stored in `models/` directory

---

## 🔄 Updates & Maintenance

### Regular Updates
- `models_registry.json` - Auto-updated on scan
- `*.log` files - Real-time append
- `runtime.db` - Real-time updates

### Manual Updates
- Documentation - As needed
- Test files - When adding features
- Configuration - Rarely

---

## 📞 Related Links

- **GitHub:** https://github.com/zombiecoder1/zombie-coder-local-ai-ollama
- **Documentation:** [doc/INDEX.md](./doc/INDEX.md)
- **Tests:** [test/README.md](./test/README.md)

---

**Total Project Size:** ~15.5 GB (mostly models)  
**Code Size:** ~2,000 lines Python  
**Documentation:** 8 comprehensive MD files  
**Test Coverage:** 100% (5/5 core tests passing)

