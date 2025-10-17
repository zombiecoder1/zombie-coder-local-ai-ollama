# 🧪 টেস্টিং গাইড - Testing Guide

**ZombieCoder Local AI Framework**

এই গাইড দেখাবে কিভাবে testui.html এবং অন্যান্য test tools ব্যবহার করে সিস্টেম test করবেন।

---

## 📋 Table of Contents

1. [সার্ভার চালু করা](#সার্ভার-চালু-করা)
2. [Test UI ব্যবহার](#test-ui-ব্যবহার)
3. [API Endpoints টেস্ট](#api-endpoints-টেস্ট)
4. [Model Testing](#model-testing)
5. [Automated Tests](#automated-tests)

---

## 🚀 সার্ভার চালু করা

### Step 1: Server Start
```bash
# Terminal খুলুন
cd C:\model

# Server চালু করুন
python model_server.py
```

**Expected Output:**
```
INFO: Uvicorn running on http://0.0.0.0:8155
INFO: Started server process
INFO: Waiting for application startup
INFO: Application startup complete
```

### Step 2: Verify Server Running
```bash
# নতুন terminal খুলে চেক করুন
curl http://localhost:8155/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "ZombieCoder Local AI Framework",
  "version": "0.1.0",
  "port": 8155
}
```

✅ যদি এই response পান = Server সঠিকভাবে চালু আছে!

---

## 🌐 Test UI ব্যবহার

### Method 1: Direct File Open (সহজ)

```bash
# Browser এ সরাসরি খুলুন
file:///C:/model/test/testui.html
```

### Method 2: Test Server দিয়ে (Recommended)

```bash
# Test UI server চালু করুন
cd C:\model\test
python testui.py
```

তারপর browser এ খুলুন: **http://localhost:8080**

---

## 🎯 Test UI Features

### 1. System Information Card
**যা দেখাবে:**
- CPU model
- RAM size
- GPU information
- OS version
- System tier (entry_level/good/high_end)

**API:**
```bash
GET http://localhost:8155/system/info
```

**Test করুন:**
- "Refresh Server Data" button click করুন
- System info update হবে

---

### 2. Models Card

**যা দেখাবে:**
- **Installed Models:** যে models download করা আছে
- **Available Models:** যে models download করা যাবে

**APIs:**
```bash
GET http://localhost:8155/models/installed
GET http://localhost:8155/models/available
```

**Test করুন:**
- Refresh করলে model list update হবে
- Model chips click করা যাবে

---

### 3. Chat Interface

**Features:**
- Message input box
- Send button
- Chat history
- Current model indicator

**কিভাবে test করবেন:**

#### Option A: Simulated (Default)
```
1. Message box এ কিছু লিখুন
2. Send click করুন
3. Simulated response পাবেন
```

#### Option B: Real Model (Recommended)

**Step 1:** Model load করুন
```bash
curl -X POST http://localhost:8155/runtime/load/tinyllama-gguf?threads=4
```

**Step 2:** testui.html এ code uncomment করুন
- `sendMessage()` function এ যান
- "REAL API CALL" section uncomment করুন
- "SIMULATED RESPONSE" section comment out করুন

**Step 3:** Chat করুন
```
1. Message box এ লিখুন: "Write Python hello world"
2. Send click করুন
3. Real model response পাবেন 3-5 সেকেন্ডে
```

**API Call:**
```bash
POST http://localhost:8155/api/generate
Content-Type: application/json

{
  "model": "tinyllama-gguf",
  "prompt": "Your message here"
}
```

---

### 4. Auto Chat Questions

**Pre-defined questions:**
- Write a Python hello world program
- Explain machine learning in simple terms
- What is FastAPI and why use it?
- Create a function to calculate factorial
- Explain async/await in Python

**Test করুন:**
- যেকোনো button click করুন
- Question automatically chat এ যাবে
- Response পাবেন (simulated বা real)

---

### 5. Footer - Endpoints Monitor

**যা monitor করা হয়:**

| Endpoint | URL | Check Interval |
|----------|-----|----------------|
| Main Server | http://127.0.0.1:8155 | 5 seconds |
| Health | /health | 5 seconds |
| System Info | /system/info | 5 seconds |
| Models Installed | /models/installed | 5 seconds |
| Models Available | /models/available | 5 seconds |

**Status Indicators:**
- 🟢 Green dot + "Online" = Server responding
- 🔴 Red dot + "Offline" = Server not responding

**Interactive Features:**
- **Copy button:** URL clipboard এ copy করে
- **Status button:** Manual refresh করে status check
- **Toggle button:** Footer hide/show করে
- **Reset button:** Layout reset করে

---

## 🔍 API Endpoints টেস্ট

### Manual Testing (cURL)

#### 1. Health Check
```bash
curl http://localhost:8155/health
```

**Expected:** `{"status":"healthy",...}`

#### 2. System Info
```bash
curl http://localhost:8155/system/info
```

**Expected:** CPU, RAM, GPU info

#### 3. Models Installed
```bash
curl http://localhost:8155/models/installed
```

**Expected:** List of installed models

#### 4. Models Available
```bash
curl http://localhost:8155/models/available
```

**Expected:** Recommended models for your tier

#### 5. Runtime Status
```bash
curl http://localhost:8155/runtime/status
```

**Expected:** Currently loaded models

---

## 🤖 Model Testing

### Complete Model Test Flow

#### Step 1: Check Available Models
```bash
curl http://localhost:8155/models/installed
```

**Find a GGUF model (e.g., tinyllama-gguf)**

#### Step 2: Load Model
```bash
curl -X POST "http://localhost:8155/runtime/load/tinyllama-gguf?threads=4"
```

**Expected Response:**
```json
{
  "status": "ready",
  "model": "tinyllama-gguf",
  "port": 8080,
  "pid": 12345
}
```

**Wait:** 3-4 seconds

#### Step 3: Check Runtime Status
```bash
curl http://localhost:8155/runtime/status
```

**Expected:**
```json
{
  "models": [
    {
      "model": "tinyllama-gguf",
      "status": "ready",
      "port": 8080
    }
  ]
}
```

#### Step 4: Generate Text
```bash
curl -X POST http://localhost:8155/api/generate \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"tinyllama-gguf\",\"prompt\":\"Write hello world Python\"}"
```

**Expected:** Model generated response (3-5 seconds)

#### Step 5: Unload Model
```bash
curl -X POST http://localhost:8155/runtime/unload/tinyllama-gguf
```

**Expected:**
```json
{
  "status": "stopped",
  "model": "tinyllama-gguf"
}
```

---

## 🧪 Automated Tests

### Run Core Tests

```bash
cd C:\model\test
python run_core_tests.py
```

**Expected Output:**
```
[1/5] Testing: 01_preflight_check
✓ PASS (0.9s)

[2/5] Testing: 02_model_lifecycle
✓ PASS (6.5s)

[3/5] Testing: 03_api_standard_check
✓ PASS (0.9s)

[4/5] Testing: 04_ui_data_integrity
✓ PASS (1.1s)

[5/5] Testing: 05_integrated_session_test
✓ PASS (7.2s)

Success Rate: 100.0%
```

---

### Run Individual Tests

```bash
# Preflight check
python test/01_preflight_check.py

# Model lifecycle
python test/02_model_lifecycle.py

# API standard check
python test/03_api_standard_check.py
```

---

### Integration Demo

```bash
cd C:\model\test
python demo_integration.py
```

**এই demo দেখাবে:**
- All services status
- AI text generation
- System integration examples

---

## 📊 Expected Performance

### Load Times
- TinyLlama (Q2_K): **3-4 seconds**
- Phi-2 (Q4_K): **5-7 seconds**
- Larger models: **10-15 seconds**

### Generation Speed
- CPU (4 threads): **10-15 tokens/second**
- CPU (8 threads): **15-20 tokens/second**
- GPU accelerated: **100+ tokens/second**

### API Latency
- Health check: **<50ms**
- Model list: **<100ms**
- System info: **<100ms**
- Generate (64 tokens): **3-5 seconds**

---

## ❌ Common Issues & Solutions

### Issue 1: Server Not Responding
**Symptoms:** All endpoints showing offline

**Solution:**
```bash
# Check if server running
curl http://localhost:8155/health

# If not, start server
python model_server.py
```

---

### Issue 2: Model Not Found (404)
**Symptoms:** `/runtime/load/{model}` returns 404

**Solution:**
```bash
# Check installed models
curl http://localhost:8155/models/installed

# Download a GGUF model
curl -X POST http://localhost:8155/download/start \
  -d '{"model_name":"tinyllama-gguf","repo_id":"TheBloke/TinyLlama-1.1B-Chat-GGUF"}'
```

---

### Issue 3: Model Not Loaded (409)
**Symptoms:** `/api/generate` returns 409 Conflict

**Solution:**
```bash
# Load model first
curl -X POST http://localhost:8155/runtime/load/tinyllama-gguf
```

---

### Issue 4: Chat Not Working in UI
**Symptoms:** Simulated response only, no real AI

**Solution:**
1. Open `testui.html` in text editor
2. Find `sendMessage()` function
3. Uncomment "REAL API CALL" section
4. Comment out "SIMULATED RESPONSE" section
5. Make sure model is loaded
6. Refresh browser

---

## ✅ Test Checklist

### Before Testing:
- [ ] Server running at port 8155
- [ ] At least one GGUF model installed
- [ ] llama.cpp runtime available

### Test UI Features:
- [ ] System info displays correctly
- [ ] Models list shows installed models
- [ ] Refresh button works
- [ ] Endpoints monitor shows status
- [ ] Clock updates every second
- [ ] Copy URL works
- [ ] Chat interface accepts input

### Test API with Real Model:
- [ ] Load model successfully
- [ ] Runtime status shows "ready"
- [ ] Generate text works
- [ ] Response time acceptable (<10s)
- [ ] Unload model successfully

### Test Automated Suite:
- [ ] All 5 core tests pass
- [ ] Duration under 30 seconds
- [ ] No errors in output
- [ ] JSON reports generated

---

## 📞 Need Help?

### Check Logs:
```bash
# Server logs
cat C:\model\logs\server.log

# Runtime logs
cat C:\model\logs\runtime_tinyllama-gguf.log
```

### Debug Mode:
```bash
# Add to model_server.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Reports:
```bash
# Check test results
cat C:\model\test\core_test_report.json
```

---

## 🎯 Quick Reference

### Start Testing (3 commands):
```bash
# 1. Start server
cd C:\model && python model_server.py

# 2. (New terminal) Load model
curl -X POST http://localhost:8155/runtime/load/tinyllama-gguf

# 3. Open test UI
start http://localhost:8080  # or file:///C:/model/test/testui.html
```

### Stop Testing:
```bash
# 1. Unload model
curl -X POST http://localhost:8155/runtime/unload/tinyllama-gguf

# 2. Stop server
# Press Ctrl+C in server terminal
```

---

## 📝 Test Report Template

```markdown
# Test Session Report

Date: 2025-10-18
Tester: Your Name

## Environment
- OS: Windows 10
- RAM: 16 GB
- Model: tinyllama-gguf

## Tests Performed
- [ ] Server health check
- [ ] System info API
- [ ] Models list API
- [ ] Model load
- [ ] Text generation
- [ ] Model unload

## Results
✓ All tests passed
Duration: 25 seconds

## Issues Found
None

## Performance
- Load time: 3.5s
- Generation: 14 tokens/sec
- API latency: <100ms
```

---

**সফল Testing এর জন্য শুভকামনা!** 🎉

**Questions?** Contact: infi@zombiecoder.my.id

