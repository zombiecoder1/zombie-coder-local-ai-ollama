A. সিস্টেম আরকিটেকচার ও নীতিমালা (উচ্চ স্তর)

Provider Core

একটিই সার্ভার (C:\model) — সব মডেল, কনফিগ, ডকুমেন্ট, টেস্ট এখানে থাকবে।

সার্ভার Ollama-কমপ্যাটিবল এন্ডপয়েন্ট প্রদান করবে: /api/tags, /api/generate, /api/chat, /runtime/load/{model}, /runtime/unload/{model}, /models/installed, /download/start ইত্যাদি।

Editor/Agent (VSCode, Cursor, Zed, CLI) — এই এন্ডপয়েন্টগুলো কল করবে, এবং সার্ভার smartly মডেল সিলেক্ট/লজি-লোড করবে।

Ollama as fallback

যদি কোন প্রজেক্টে Ollama ইন্টিগ্রেশন থাকে, তুমি ওগুলো ছুঁড়ে দিবা না। তোমার সার্ভার Ollama-স্টাইল কল গ্রহণ করবে—এবং যদি তোমার মডেল তালিকায় থাকে, উত্তর দিবে, না থাকলে (অপশনাল) Ollama upstream ব্যবহার করবে।

অর্থাৎ তোমার সার্ভার “primary provider” হবে; Ollama হবে optional upstream.

Persistent Lazy-Load (sleep/keep-loaded)

মডেল প্রথমবার লোড হলে RAM-এ বসবে এবং “sleep/idle” মোডে থাকবে (active=false কিন্তু resident)।

অনুরোধ এলে সরাসরি রিপন্ড করবে (cold start latency কমাতে)।

Unload কেবলমাত্র যখন সিস্টেমটা memory pressure অনুভব করবে বা explicit admin/unload করা হবে।

কনফিগে keep_loaded: true/false এবং idle_timeout_seconds থাকবে (default: keep_loaded=true, idle_timeout=86400)

Process robustness (Python process কিল করা যাবে না)

Windows পরিবেশে Python process কে সার্ভিস হিসেবে চালাও (NSSM / sc create) — যাতে কেউ সহজে Ctrl+C/kill না করতে পারে।

সার্ভারকে system service বানালে auto-restart এবং recovery সেট করা যাবে।

পাশাপাশি একটি small watchdog (Python) চালাও যা process unexpectedly বন্ধ হলে auto-restart করবে।

পর্যায়ক্রমে clean shutdown/backup করাতে হবে (git commit before changes).

Dev hygiene: tests & docs

C:\model\test — সব টেস্ট ফাইল এখানে রাখবে।

C:\model\documentation — সব ডকুমেন্ট, API spec, modelfiles, README এখানে neatly organize করবে।

git repo root = C:\model → প্রতিটি পরিবর্তনের আগে commit করে রাখতে হবে।

B. Agent-ready কাজের (অ্যাকশন লিস্ট — এজেন্ট সরাসরি করার যোগ্য)

এগুলো এজেন্টকে কপি-পেস্ট করে দেবো — এজেন্ট এগুলো স্টেপ বাই স্টেপ চালাবে, রিপোর্ট তৈরি করবে, এবং অনুমোদন চাইবে যেখানে দরকার।

Agent Tasklist: ZombieCoder Provider Setup (Full Provider Ecosystem)

1. Directory & repo setup
   - Ensure base dir: C:\model exists.
   - Create folders if missing:
     - C:\model\test
     - C:\model\documentation
     - C:\model\models
     - C:\model\scripts
     - C:\model\logs
   - If .git not present in C:\model -> initialize git:
     - git init
     - git add .
     - git commit -m "initial snapshot before provider changes"

2. Ensure installed models are discoverable:
   - Scan C:\model\models for subfolders containing .gguf files.
   - Build models index JSON: C:\model\registry\models_index.json

3. Expose Ollama-compatible endpoints (if missing), or verify:
   - GET  /api/tags -> return models list (name, path, size, status)
   - POST /api/generate -> standard generate (model param optional)
   - POST /api/chat -> chat-based API (messages array)
   - POST /runtime/load/{model} -> force load
   - POST /runtime/unload/{model} -> force unload
   - GET  /models/installed -> same as /api/tags (for editors)
   - POST /download/start -> start HF download, provide progress

4. Implement model manager (stateful):
   - For each model maintain: { name, path, status: unloaded/loaded, last_used_ts, keep_loaded }
   - On request with "model": "<name>":
       a) resolve best-match model folder (fuzzy match)
       b) if not loaded -> load model with lazy-load flags
       c) mark last_used_ts and return
   - keep_loaded default: true (so model remains resident after load)
   - Implement LRU eviction only when total_ram_usage > threshold (configurable)

5. Lazy-load test behavior:
   - After first load, keep model in memory (sleep/idle) — ensure not garbage-collected or unloaded by default.
   - idle-unload only if manual admin request or memory high.

6. Robustness: run server as Windows service + watchdog:
   - Install NSSM (or use sc create) to run python -m uvicorn model_server:app as a service.
   - Create a watchdog script (scripts/watchdog.py) that ensures server process running; restart if dead.
   - Setup Windows service recovery: restart on failure (NSSM supports)

7. Development workflow enforcement:
   - All changes must be committed to git before applying (create branch feature/provider-setup).
   - Tests must be placed into C:\model\test and documentation into C:\model\documentation before deployment.
   - Agent must run tests and save test results under C:\model\logs/test_results_TIMESTAMP.json

8. Safety & approval:
   - Agent will NOT delete any model file without explicit user approval.
   - Agent will prepare "safe_to_delete" list and ask user.
   - Agent will produce final migration report at C:\model\MODEL_MIGRATION_SUMMARY.md

9. Reporting:
   - After tasks complete, produce:
     - C:\model\registry\models_index.json
     - C:\model\logs/provider_setup_report.json
     - C:\model\MODEL_MIGRATION_SUMMARY.md
   - Notify user for approval for any destructive ops.

C. কনফিগ ও কমান্ড স্নিপেট (তুমিই চালাবে বা এজেন্ট চালাবে)
1) সার্ভার কনফিগ (example C:\model\config\provider_config.json)
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

2) service 설치 (Windows, NSSM) — PowerShell example

(먼 আগে nssm.exe ডাউনলোড করে C:\tools\nssm\nssm.exe রাখ)

# install service
C:\tools\nssm\nssm.exe install ZombieCoderAI "C:\model\.venv\Scripts\python.exe" "-m uvicorn model_server:app --host 0.0.0.0 --port 8007"
# set recovery: restart on failure
C:\tools\nssm\nssm.exe set ZombieCoderAI AppRestartDelay 5000
C:\tools\nssm\nssm.exe start ZombieCoderAI

3) Watchdog minimal (scripts/watchdog.py)
import time, subprocess, psutil, os
SERVICE_NAME = "ZombieCoderAI"
while True:
    found = False
    for p in psutil.process_iter(['pid','name','cmdline']):
        if 'uvicorn' in ' '.join(p.info.get('cmdline',[])):
            found = True
            break
    if not found:
        # try to start via NSSM or direct
        subprocess.Popen(["C:\\tools\\nssm\\nssm.exe", "start", SERVICE_NAME])
    time.sleep(10)


(এজেন্ট এটি ইনস্টল ও চালাবে; service recovery সেটিংসও লাগবে)

4) models index schema (C:\model\registry\models_index.json)
{
  "models": [
    {
      "name": "qwen2.5-1.5b-instruct",
      "path": "models\\qwen2.5-1.5b-instruct-gguf\\qwen2.5-1.5b-instruct-q4_k_m.gguf",
      "size_bytes": 1180000000,
      "status": "loaded",
      "keep_loaded": true
    }
  ]
}

5) Editor integration example (Client side)

VS Code extension / any agent calls:

POST http://127.0.0.1:8007/api/chat
Content-Type: application/json
x-api-key: zombie-local-please-change

{
  "model": "qwen2.5-1.5b-instruct",
  "messages": [{"role":"user","content":"Write a small helper in Python to parse CSV"}],
  "max_tokens": 300
}

Final checklist (তোমার কাছে পাঠাবার আগে এজেন্টে enforce করাও)

 C:\model\test ফোল্ডারে test-case files রাখো (unit tests, prompts)

 C:\model\documentation এ সব README, API spec, modelfiles docs রাখো

 git init + প্রথম commit রাখা আছে (revert সহজ হবে)

 Service (NSSM) ইনস্টল ও চালু আছে (ZombieCoderAI)

 Watchdog চালু আছে

 Provider endpoints functional: /api/tags, /api/generate, /api/chat

 keep_loaded: true default, idle-unload policy ঠিক আছে

 Agent রিপোর্ট ফাইল: C:\model\logs\provider_setup_report.json তৈরি হবে