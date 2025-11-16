✅ 1. তোমার উদ্দেশ্য (এজেন্টের জন্য স্পষ্টভাবে লেখা)

এজেন্ট, তোমার প্রধান দায়িত্ব হলো ZombieCoder Provider Ecosystem-কে এমনভাবে সাজানো:

Ollama Fallback থাকবে

অন্য কোনো প্রজেক্ট যেগুলো ইতিমধ্যে Ollama ব্যবহার করে

তাদের কোড না বদলিয়েই তোমার সার্ভার Ollama API style request হ্যান্ডেল করবে

কিন্তু মডেল রেসপন্স দেবে ZombieCoder Provider server

ZombieCoder Provider হবে প্রাইমারি সার্ভার

VS Code Local Copilot

Cursor AI

Zed AI

Browser Agents

CLI Tools
সবগুলোই ZombieCoder Provider API ব্যবহার করবে।

মডেলগুলো সার্ভারে লোড থাকলে forever-sleep মোডে থাকবে

লোড হয়ে কয়েক সেক পরে unloading হবে না

idle হলেও resident থাকবে

unload কেবল ম্যানুয়ালি বা RAM crisis হলে

Runtime Lazy Load (Ollama style)

প্রথম কল → মডেল লোড

পরে সব কল → সেই লোডেড ইনস্ট্যান্স রেসপন্স দেবে

সার্ভার কখনো accidental kill হওয়া যাবে না

python process কে kill করলে system নিজে বন্ধ হয়ে যাবে

তাই:

server must run as Windows service

watchdog must run separately

agent python will NEVER kill process directly

✅ 2. এজেন্ট কোন ফোল্ডারে কি রাখবে (তোমার নির্দেশ অনুসারে)
📌 Test files → C:\model\test

এজেন্ট এখানে রাখবে:

model test cases

load tests

generation tests

json protocol tests

error reproduction files

📌 Documentation → C:\model\documentation

এজেন্ট এখানে রাখবে:

API specification

Provider Ecosystem overview

Ollama compatibility notes

Integration guides (VSCode, Cursor, Zed, CLI)

Model capability notes

Changelog

📌 Script → C:\model\scripts

watchdog.py

build_models_index.py

model_loader_utils.py

service_installer.ps1

📌 Registry → C:\model\registry

models_index.json

provider_metadata.json

✅ 3. Git Workflow (এজেন্টের জন্য বাধ্যতামূলক নিয়ম)

এজেন্ট, এটা অত্যন্ত গুরুত্বপূর্ণ:

🔥 নিয়ম ১:

যেকোনো পরিবর্তনের আগে Git commit অবশ্যই করতে হবে
কারণ কোনো ভুল হলে revert করা লাগবে।

🔥 নিয়ম ২:

এজেন্ট কখনোই .git ফোল্ডার মুছবে না।

🔥 নিয়ম ৩:

এজেন্ট যখন কোড/ফাইল modify করবে:

প্রথমে git add

তারপর git commit -m

তারপর কাজ শুরু

🔥 নিয়ম ৪:

এজেন্ট কখনো python runtime বন্ধ করবে না
(সার্ভার বন্ধ হলে provider system চুপসে যাবে)

✅ 4. Provider Runtime Behavior (এজেন্টকে একদম স্পষ্টভাবে)

এজেন্ট, মডেল runtime state এভাবে মেইনটেইন করবে:

✔ Lazy Load (Ollama-style):

If not loaded → auto-load

If loaded → direct use

✔ Keep Loaded:
keep_loaded_default = true
idle_unload_seconds = 86400 (1 day)

✔ Sleep Mode:

মডেল idle হলে unload না করে “sleep” অবস্থায় memory resident থাকবে।

✔ Multi-model support:

একাধিক মডেল একসঙ্গে লোড থাকতে পারবে
(based on RAM threshold)

✅ 5. এখন তোমাকে (জম্বি ভাই) যা করতে হবে
A) সার্ভারকে Windows Service বানানো

যাতে accidental close/on/off হয় না:

PowerShell:

nssm install ZombieCoderAI "C:\model\.venv\Scripts\python.exe" "-m uvicorn model_server:app --host 0.0.0.0 --port 8007"
nssm set ZombieCoderAI AppRestartDelay 5000
nssm start ZombieCoderAI

B) watchdog চালু করা
python C:\model\scripts\watchdog.py

C) এজেন্টকে চালিয়ে দেওয়া

নিচে পুরো এজেন্ট টাস্ক স্কোপ দেওয়া হলো—কপি করে তার কাছে দাও।

📦 6. এজেন্টকে দেওয়ার চূড়ান্ত নির্দেশনা (কপি করে ওকে দেবে)
Agent Instructions (ZombieCoder Provider Mode)

1. DO NOT kill python runtime or uvicorn process.
2. DO NOT stop the ZombieCoderAI Windows service.
3. Place test files ONLY inside: C:\model\test
4. Place documentation ONLY inside: C:\model\documentation
5. ALWAYS commit before modifying any file:
      git add .
      git commit -m "checkpoint"

6. Maintain model runtime as:
      keep_loaded = true
      idle_unload_seconds = 86400
      never auto-unload

7. Ensure model auto-load on generate/chat request.
8. Ensure sleep-mode (resident in RAM) after load.
9. Never delete any model without explicit approval.
10. Keep registry/models_index.json updated.

11. Ensure all provider endpoints are functional:
      /api/tags
      /api/generate
      /api/chat
      /runtime/load/{model}
      /models/installed

12. Write no new files outside:
      C:\model\test
      C:\model\documentation
      C:\model\scripts
      C:\model\registry
      C:\model\config
      C:\model\logs

13. Log every action inside: C:\model\logs

14. When confused: ask user before changing anything.

🔥 এক লাইনে তোমার সিস্টেম এখন কোথায় দাঁড়ায়

তোমার সার্ভার এখন Ollama-এর জায়গায় দাঁড়াতে পারবে, fallback হিসেবে Ollama ব্যবহার করতে পারবে,
এবং VS Code, Cursor, Zed, CLI সব কিছুর জন্য একটি Full Provider Ecosystem হিসেবে কাজ করবে।