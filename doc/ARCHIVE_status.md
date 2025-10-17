# ZombieCoder Local AI Framework — Status & Activation Plan (FINAL)

তারিখ: (লোকাল সময় অনুযায়ী) আপডেটেড

## উদ্দেশ্য
- অফলাইন‑ফার্স্ট লোকাল AI সার্ভার: Lazy Load (llama.cpp), Orchestration, Proxy (/api/generate), এবং ডাইনামিক UI।

## এখন পর্যন্ত সম্পন্ন (DONE)
- API Gateway (FastAPI) চালু: `/health`, `/system/info`, `/models/installed`, `/models/available`।
- Runtime Orchestrator: `/runtime/status`, `/runtime/load/{model}`, `/runtime/unload/{model}`, `/runtime/config`।
- Proxy Generate: `/api/generate` → চলমান llama.cpp সার্ভারের `/completion` এ প্রক্সি।
- Downloader: `/download/start|status|cancel` (রিয়েল লগ `models/download_<name>.log`)।
- UI ডাইনামিক: `static/index.html` → Health/System/Tier, Installed+Runtime (Load/Unload), Available+Download, Test Chat (/api/generate)।
- Persistency: `data/runtime.db` এ runtime state সংরক্ষণ (restart‑safe)।
- Tests (C:\model\test): `01_preflight_check.py`, `02_model_lifecycle.py`, `03_api_standard_check.py`, `04_ui_data_integrity.py`।
- Tiny model installed: `C:\model\models\tinyllama` (~342 MB) সাফল্যের সঙ্গে ডাউনলোড ও রেজিস্ট্রি‑ডিটেক্টেড।
 - Idle Killer (10m inactivity auto-unload) + Graceful shutdown যোগ।
 - Session API: `/api/session/start|status|end`।
 - VRAM/GPU Detection (`system_detector.py`) এবং `--gpu-layers` heuristic (`router.py`)।
 - `/api/tags` Ollama-like প্রসারিত: status/runtime_status/format/quantization/size।

## বর্তমান অবস্থা
সব কোর ফিচার সক্রিয়; GGUF মডেল (qwen0_5b) দিয়ে Load→Generate→Unload সফল।

## কী করলে ব্লকার দূর হবে (REQUIRED ACTION)
কোনো ব্লকার নেই।

## চূড়ান্ত অ্যাক্টিভেশন রান স্ট্যাটাস
| টেস্ট স্ক্রিপ্ট | স্ট্যাটাস | মূল প্রমাণ |
| :--- | :--- | :--- |
| `01_preflight_check.py` | ✅ PASSED | Health OK, runtime_ready=true |
| `02_model_lifecycle.py` | ✅ PASSED | Load READY, Generate 200, Unload COMPLETE |
| `03_api_standard_check.py` | ✅ PASSED | `/api/tags` PASS, unloaded generate=409 |
| `04_ui_data_integrity.py` | ✅ PASSED | UI data valid |
| `05_integrated_session_test.py` | ✅ PASSED | Session start→generate→status→unload OK |

## টাস্ক ট্র্যাক (Checklist)
- [x] API + Orchestrator + Proxy + UI + Downloader + Persistency
- [x] Tiny model + GGUF model (qwen0_5b)
- [x] server.exe placed at `C:\model\config\llama.cpp\server.exe`
- [x] Activation tests 01‑05 run + proofs (JSON + server.log tail)

## আমার প্রয়োজনীয় অনুমতি/ইনপুট
কিছু নেই।

## এজেন্ট স্বাক্ষর ও যাচাইকরণ (Agent Signatures)
| এজেন্ট | ভূমিকা | স্বাক্ষর সময় |
| :--- | :--- | :--- |
| **ZombieCoder-Orchestrator (GPT-5 @ Cursor)** | GGUF Load/Unload, Proxy, Tests | (auto)


