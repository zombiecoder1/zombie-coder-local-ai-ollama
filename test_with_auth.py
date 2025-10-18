#!/usr/bin/env python3
"""
ZombieCoder - Authentication Test Script
টোকেন সহ সম্পূর্ণ ফ্লো টেস্ট
"""
import requests
import time
import json

BASE = "http://127.0.0.1:8155"
HF_TOKEN = "hf_YOUR_TOKEN_HERE"

def log(msg, status="info"):
    colors = {"ok": "\033[92m", "warn": "\033[93m", "err": "\033[91m", "info": "\033[96m"}
    print(f"{colors.get(status, '')}{msg}\033[0m")

def test_auth():
    log("🔑 HuggingFace Authentication Test", "info")
    
    # Step 1: Save token
    log("টোকেন সেভ করা হচ্ছে...", "info")
    try:
        r = requests.post(f"{BASE}/auth/hf_token", json={"token": HF_TOKEN}, timeout=10)
        if r.ok:
            log(f"✅ টোকেন সেভ সফল: {r.json()}", "ok")
        else:
            log(f"❌ টোকেন সেভ ব্যর্থ: {r.status_code}", "err")
            return False
    except Exception as e:
        log(f"❌ টোকেন সেভ এরর: {e}", "err")
        return False
    
    # Step 2: Check auth status
    log("অথেনটিকেশন স্ট্যাটাস চেক...", "info")
    try:
        r = requests.get(f"{BASE}/auth/status", timeout=10)
        if r.ok:
            data = r.json()
            log(f"✅ Auth Status: {data}", "ok")
            if data.get('token_set'):
                log("✅ টোকেন সেট করা আছে", "ok")
                return True
            else:
                log("❌ টোকেন সেট করা নেই", "err")
                return False
        else:
            log(f"❌ Auth status check ব্যর্থ: {r.status_code}", "err")
            return False
    except Exception as e:
        log(f"❌ Auth status এরর: {e}", "err")
        return False

def main():
    log("═══════════════════════════════════════", "info")
    log("  ZombieCoder - Authentication Test", "info")
    log("═══════════════════════════════════════", "info")
    
    # Test server health first
    try:
        r = requests.get(f"{BASE}/health", timeout=5)
        if r.ok:
            log(f"✅ সার্ভার প্রস্তুত: {r.json().get('status')}", "ok")
        else:
            log("❌ সার্ভার বন্ধ", "err")
            return
    except:
        log("❌ সার্ভার অ্যাক্সেস করা যাচ্ছে না", "err")
        return
    
    # Run auth test
    log(f"\n🧪 Authentication টেস্ট...", "info")
    result = test_auth()
    
    # Summary
    log("\n═══════════════════════════════════════", "info")
    log("  টেস্ট রেজাল্ট", "info")
    log("═══════════════════════════════════════", "info")
    
    if result:
        log("🎉 Authentication টেস্ট সফল!", "ok")
        log("💡 টোকেন সেট করুন: hf_YOUR_TOKEN_HERE → আপনার আসল টোকেন", "info")
    else:
        log("⚠️ Authentication টেস্ট ব্যর্থ।", "warn")
        log("💡 টোকেন সেট করুন: hf_YOUR_TOKEN_HERE → আপনার আসল টোকেন", "info")

if __name__ == "__main__":
    main()
