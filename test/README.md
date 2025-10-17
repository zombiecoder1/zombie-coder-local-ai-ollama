# ZombieCoder Local AI - Test Suite

এই ফোল্ডারে ZombieCoder Local AI Framework-এর সম্পূর্ণ টেস্ট স্যুট রয়েছে।

## Test Files

### Core Tests (01-05)
এই টেস্টগুলো সিস্টেমের মূল functionality যাচাই করে:

1. **01_preflight_check.py** - প্রাথমিক সিস্টেম চেক
   - Health endpoint
   - Runtime configuration
   - GGUF model detection

2. **02_model_lifecycle.py** - মডেল লাইফসাইকেল টেস্ট
   - Model load
   - Inference (text generation)
   - Model unload

3. **03_api_standard_check.py** - API compatibility
   - Ollama-compatible endpoints
   - `/api/tags` format validation

4. **04_ui_data_integrity.py** - UI data validation
   - System info accuracy
   - Model list integrity
   - Runtime status tracking

5. **05_integrated_session_test.py** - Session management
   - Session creation
   - Model operations with session
   - Session state verification

### Verification Scripts (06-07)
বিস্তারিত সিস্টেম যাচাইকরণ:

6. **06_verify_system.py** - সিস্টেম যাচাইকরণ
   - Log analysis
   - Endpoint verification
   - Ollama server check
   - Model list validation

7. **07_gguf_model_test.py** - GGUF মডেল টেস্ট
   - GGUF model download
   - Load with timeout
   - Inference test
   - Unload verification

### Test Runner
- **run_all_tests.py** - সব টেস্ট একসাথে চালায়
- **test_report.json** - বিস্তারিত টেস্ট রিপোর্ট
- **TEST_SUMMARY.md** - সম্পূর্ণ টেস্ট সামারি

### UI Test
- **testui.html** - ব্রাউজার-based টেস্ট UI
- **testui.py** - UI সার্ভার

---

## কিভাবে টেস্ট চালাবেন

### Prerequisites
- সার্ভার চালু থাকতে হবে: `python model_server.py`
- কমপক্ষে একটি GGUF মডেল ইনস্টল থাকতে হবে

### একক টেস্ট চালানো

```bash
cd C:\model\test
python 01_preflight_check.py
```

### সব টেস্ট একসাথে চালানো

```bash
cd C:\model\test
python run_all_tests.py
```

### Core Tests শুধুমাত্র

```bash
cd C:\model\test
python 01_preflight_check.py && python 02_model_lifecycle.py && python 03_api_standard_check.py && python 04_ui_data_integrity.py && python 05_integrated_session_test.py
```

---

## Test Output Format

সব টেস্ট JSON ফরম্যাটে output দেয়:

```json
{
  "ok": true,
  "checks": {...},
  "steps": [...]
}
```

- `ok: true` = টেস্ট পাস
- `ok: false` = টেস্ট ফেইল

Exit code:
- `0` = পাস
- `1` = ফেইল

---

## Expected Results

### ✅ All Core Tests Should Pass

```
01_preflight_check.py     ✓ PASS (0.9s)
02_model_lifecycle.py     ✓ PASS (4.2s)
03_api_standard_check.py  ✓ PASS (1.0s)
04_ui_data_integrity.py   ✓ PASS (1.3s)
05_integrated_session_test.py ✓ PASS (8.5s)
```

**Total Duration:** ~16 seconds  
**Success Rate:** 100%

---

## Test Requirements

### Required Models
- কমপক্ষে একটি **GGUF format** মডেল প্রয়োজন
- Recommended: `tinyllama-gguf` (8.1 GB)

### System Requirements
- Windows 10+
- Python 3.8+
- llama.cpp runtime installed
- 8GB+ RAM
- 10GB+ free disk space

---

## Troubleshooting

### "Model not found" Error
- নিশ্চিত করুন GGUF মডেল ইনস্টল আছে
- চেক করুন: `curl http://localhost:8155/models/installed`

### "Runtime not ready" Error
- নিশ্চিত করুন llama.cpp binary আছে: `C:\model\config\llama.cpp\server.exe`

### Timeout Errors
- মডেল লোড হতে 30-40 সেকেন্ড লাগতে পারে
- প্রথম বার chache build হতে বেশি সময় লাগে

### Port Already in Use
- অন্য instance বন্ধ করুন
- Port পরিবর্তন করুন: `MODEL_SERVER_PORT=8156 python model_server.py`

---

## Test Coverage

### Tested Components
- ✅ API Gateway (FastAPI)
- ✅ Runtime Orchestrator
- ✅ Model Loading/Unloading
- ✅ Text Generation (Inference)
- ✅ Session Management
- ✅ Download Manager
- ✅ System Detection
- ✅ Model Registry

### Tested Scenarios
- ✅ Cold start (first load)
- ✅ Concurrent requests
- ✅ Session tracking
- ✅ Error handling
- ✅ Timeout management
- ✅ Port allocation
- ✅ Process lifecycle

---

## Continuous Testing

### Run Tests Automatically
একটি cron job বা scheduled task সেট করতে পারেন:

```bash
# Windows Task Scheduler
# Run: C:\model\test\run_all_tests.py
# Schedule: Daily at 2 AM
```

### Monitor Test Results
Test reports save হয় `test_report.json`-এ। এটি parse করে monitoring করতে পারেন।

---

## Contributing

নতুন টেস্ট যোগ করতে:
1. `08_your_test.py` নামে ফাইল তৈরি করুন
2. JSON output format follow করুন
3. Exit code 0 (pass) বা 1 (fail) return করুন
4. `run_all_tests.py` automatically detect করবে

---

## Support

সমস্যা হলে:
1. `test_report.json` চেক করুন
2. `C:\model\logs\server.log` দেখুন
3. Runtime log: `C:\model\logs\runtime_*.log`

---

**Last Updated:** 2025-10-18  
**Test Suite Version:** 1.0  
**Status:** ✅ All Core Tests Passing

