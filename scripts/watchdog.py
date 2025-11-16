#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Watchdog script for ZombieCoder Provider Ecosystem
"""

import time
import subprocess
import psutil
import os

SERVICE_NAME = "ZombieCoderAI"

def is_server_running():
    """Check if the server process is running"""
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'uvicorn' in ' '.join(p.info.get('cmdline', [])):
            return True
    return False

def start_server():
    """Start the server via NSSM"""
    try:
        subprocess.Popen(["C:\\tools\\nssm\\nssm.exe", "start", SERVICE_NAME])
        print(f"✅ Attempted to start service: {SERVICE_NAME}")
    except Exception as e:
        print(f"❌ Error starting service: {e}")

def main():
    """Main watchdog loop"""
    print("🤖 ZombieCoder Watchdog Started")
    print("==============================")
    
    while True:
        if not is_server_running():
            print("⚠️  Server not running, attempting to start...")
            start_server()
        else:
            print("✅ Server is running")
        
        # Wait 10 seconds before next check
        time.sleep(10)

if __name__ == "__main__":
    main()