#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Dual Runtime System"""

import requests
import json
import time

BASE_URL = "http://localhost:8155"

print("=" * 70)
print("Testing Dual Runtime System (GGUF + SafeTensors)")
print("=" * 70)

# Test 1: Validate all models
print("\n1️⃣ Model Format Validation:")
print("-" * 70)

models = ["phi-2", "tinyllama", "tinyllama-gguf"]
validations = {}

for model in models:
    try:
        r = requests.get(f"{BASE_URL}/registry/validate/{model}", timeout=5)
        val = r.json()
        validations[model] = val
        
        status = "✅" if val.get("valid") else "❌"
        print(f"\n{status} {model}:")
        print(f"   Format: {val.get('format', 'unknown')}")
        print(f"   Valid: {val.get('valid', False)}")
        print(f"   Files: {len(val.get('files', []))} detected")
        print(f"   Message: {val.get('message', '')}")
    except Exception as e:
        print(f"\n❌ {model}: Error - {e}")

# Test 2: Try to load phi-2 (SafeTensors)
print("\n\n2️⃣ Loading SafeTensors Model (phi-2):")
print("-" * 70)

try:
    print("Attempting to load phi-2 (SafeTensors format)...")
    r = requests.post(f"{BASE_URL}/runtime/load/phi-2?threads=4", timeout=30)
    result = r.json()
    
    if r.status_code == 200:
        print(f"✅ Load initiated:")
        print(f"   Status: {result.get('status')}")
        print(f"   Format: {result.get('format', 'N/A')}")
        print(f"   Runtime: {result.get('runtime', 'N/A')}")
        print(f"   Port: {result.get('port', 'N/A')}")
        print(f"   PID: {result.get('pid', 'N/A')}")
    else:
        print(f"❌ Load failed:")
        print(json.dumps(result, indent=2))
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Check runtime status
print("\n\n3️⃣ Runtime Status:")
print("-" * 70)

try:
    r = requests.get(f"{BASE_URL}/runtime/status", timeout=5)
    status = r.json()
    
    models_running = status.get('models', [])
    print(f"Running models: {len(models_running)}")
    
    for m in models_running:
        print(f"\n   📦 {m.get('model')}:")
        print(f"      Status: {m.get('status')}")
        print(f"      Runtime: {m.get('runtime', 'unknown')}")
        print(f"      Port: {m.get('port')}")
        print(f"      PID: {m.get('pid')}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Try to load tinyllama-gguf (GGUF)
print("\n\n4️⃣ Loading GGUF Model (tinyllama-gguf):")
print("-" * 70)

try:
    print("Attempting to load tinyllama-gguf (GGUF format)...")
    r = requests.post(f"{BASE_URL}/runtime/load/tinyllama-gguf?threads=4", timeout=30)
    result = r.json()
    
    if r.status_code == 200:
        print(f"✅ Load initiated:")
        print(f"   Status: {result.get('status')}")
        print(f"   Format: {result.get('format', 'N/A')}")
        print(f"   Runtime: {result.get('runtime', 'N/A')}")
        print(f"   Port: {result.get('port', 'N/A')}")
        print(f"   PID: {result.get('pid', 'N/A')}")
        if result.get('format') == 'gguf':
            print(f"   GPU Layers: {result.get('gpu_layers', 0)}")
    else:
        print(f"❌ Load failed:")
        print(json.dumps(result, indent=2))
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Final runtime status
print("\n\n5️⃣ Final Runtime Status:")
print("-" * 70)

time.sleep(2)  # Wait for models to load

try:
    r = requests.get(f"{BASE_URL}/runtime/status", timeout=5)
    status = r.json()
    
    models_running = status.get('models', [])
    print(f"Total running models: {len(models_running)}")
    
    for m in models_running:
        print(f"\n   📦 {m.get('model')}:")
        print(f"      Status: {m.get('status')}")
        print(f"      Runtime: {m.get('runtime', 'unknown')}")
        print(f"      Port: {m.get('port')}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("Test Complete!")
print("=" * 70)

