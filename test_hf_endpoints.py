#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test HuggingFace Discovery Endpoints"""

import requests
import json

BASE_URL = "http://localhost:8155"

print("=" * 60)
print("Testing HuggingFace Discovery Endpoints")
print("=" * 60)

# Test 1: Auth whoami
print("\n1️⃣ Testing /auth/whoami")
r = requests.get(f"{BASE_URL}/auth/whoami", timeout=5)
user = r.json()
print(f"   User: {user.get('username')}")
print(f"   Email: {user.get('email')}")
print(f"   Status: {'✅ Logged in' if user.get('logged_in') else '❌ Not logged in'}")

# Test 2: Search models
print("\n2️⃣ Testing /hf/models (TinyLlama GGUF)")
r = requests.get(f"{BASE_URL}/hf/models?search=TinyLlama+GGUF&limit=5", timeout=10)
data = r.json()
print(f"   Found: {data.get('count', 0)} models")
for i, model in enumerate(data.get('models', [])[:3], 1):
    print(f"   {i}. {model['model_id']}")
    print(f"      Downloads: {model.get('downloads', 0):,}")
    print(f"      Likes: {model.get('likes', 0)}")

# Test 3: Popular models
print("\n3️⃣ Testing /hf/popular")
r = requests.get(f"{BASE_URL}/hf/popular?limit=5", timeout=10)
data = r.json()
print(f"   Found: {data.get('count', 0)} popular models")
for i, model in enumerate(data.get('models', [])[:3], 1):
    print(f"   {i}. {model['model_id']}")

# Test 4: Model files
print("\n4️⃣ Testing /hf/files (TinyLlama)")
repo_id = "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
r = requests.get(f"{BASE_URL}/hf/files/{repo_id}", timeout=10)
data = r.json()
gguf_files = data.get('gguf_files', [])
print(f"   Repo: {repo_id}")
print(f"   GGUF files: {len(gguf_files)}")
for f in gguf_files[:3]:
    print(f"   - {f['filename']}")

# Test 5: Small models
print("\n5️⃣ Testing /hf/small-models")
r = requests.get(f"{BASE_URL}/hf/small-models", timeout=10)
data = r.json()
print(f"   Found: {data.get('count', 0)} small models")
print(f"   Description: {data.get('description', '')}")
for i, model in enumerate(data.get('models', [])[:3], 1):
    print(f"   {i}. {model['model_id']}")

print("\n" + "=" * 60)
print("✅ All tests completed!")
print("=" * 60)

