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
        try:
            cmdline = p.info.get('cmdline')
            if cmdline and 'uvicorn' in ' '.join(cmdline):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Handle processes that might disappear during iteration
            pass
    return False

def start_server():
    """Start the server via NSSM"""
    try:
        subprocess.Popen(["nssm.exe", "start", SERVICE_NAME])
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