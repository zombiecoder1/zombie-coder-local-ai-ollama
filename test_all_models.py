#!/usr/bin/env python3
"""Test All Three Models - GGUF and SafeTensors"""

import requests
import json
import time

BASE = "http://localhost:8155"

print("=" * 80)
print("Testing All Three Models - Dual Runtime System")
print("=" * 80)

# Step 1: List all installed models
print("\n1️⃣ Checking Installed Models:")
print("-" * 80)

r = requests.get(f"{BASE}/registry/models")
data = r.json()
models = data.get('installed', [])

print(f"Total models found: {len(models)}\n")

for model in models:
    print(f"📦 {model['name']}")
    print(f"   Size: {model['size_mb']/1024:.2f} GB")
    print(f"   Path: {model['path']}")
    
    # Validate format
    val = requests.get(f"{BASE}/registry/validate/{model['name']}").json()
    format_icon = "⚡" if val['format'] == 'gguf' else "🐍"
    status_icon = "✅" if val['valid'] else "❌"
    
    print(f"   {status_icon} Format: {format_icon} {val['format'].upper()}")
    print(f"   Message: {val.get('message', '')}")
    print()

# Step 2: Test loading each model
print("\n2️⃣ Testing Model Loading:")
print("-" * 80)

test_models = ['tinyllama-gguf', 'phi-2', 'tinyllama']
results = {}

for model_name in test_models:
    print(f"\n🔄 Loading {model_name}...")
    try:
        r = requests.post(f"{BASE}/runtime/load/{model_name}?threads=4", timeout=30)
        result = r.json()
        
        if r.status_code == 200:
            print(f"   ✅ Load initiated")
            print(f"   Format: {result.get('format', 'N/A')}")
            print(f"   Runtime: {result.get('runtime', 'N/A')}")
            print(f"   Status: {result.get('status', 'N/A')}")
            print(f"   Port: {result.get('port', 'N/A')}")
            print(f"   PID: {result.get('pid', 'N/A')}")
            results[model_name] = 'success'
        else:
            print(f"   ❌ Load failed: {result.get('detail', result.get('message', 'Unknown error'))}")
            results[model_name] = 'failed'
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results[model_name] = 'error'
    
    time.sleep(2)

# Step 3: Check runtime status
print("\n\n3️⃣ Runtime Status:")
print("-" * 80)

time.sleep(3)  # Wait for models to load

r = requests.get(f"{BASE}/runtime/status")
status = r.json()
running = status.get('models', [])

print(f"Running models: {len(running)}\n")

for model in running:
    runtime_icon = "⚡" if model.get('runtime') == 'gguf' else "🐍"
    runtime_name = "llama.cpp" if model.get('runtime') == 'gguf' else "transformers"
    
    status_emoji = {
        'ready': '✅',
        'loading': '🔄',
        'error': '❌',
        'stopped': '⏹️'
    }.get(model.get('status', 'unknown'), '❓')
    
    print(f"{status_emoji} {model.get('model')}")
    print(f"   Runtime: {runtime_icon} {runtime_name}")
    print(f"   Status: {model.get('status', 'unknown')}")
    print(f"   Port: {model.get('port', 'N/A')}")
    print(f"   PID: {model.get('pid', 'N/A')}")
    print()

# Step 4: Summary
print("\n4️⃣ Test Summary:")
print("-" * 80)

print(f"\n📊 Load Attempts:")
for model, status in results.items():
    emoji = "✅" if status == 'success' else "❌"
    print(f"   {emoji} {model}: {status}")

print(f"\n🚀 Currently Running: {len(running)} model(s)")

# Success criteria
success_count = sum(1 for s in results.values() if s == 'success')
print(f"\n{'✅ SUCCESS!' if success_count >= 2 else '⚠️ PARTIAL'}: {success_count}/3 models loaded")

print("\n" + "=" * 80)
print("Test Complete!")
print("=" * 80)
print(f"\n🌐 Admin Panel: http://localhost:8155/static/admin/index.html")
print(f"📊 API Docs: http://localhost:8155/docs")

