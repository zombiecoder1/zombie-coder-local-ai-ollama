#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder Test Runner - Simple Interface
"""

import subprocess
import sys
import os

def main():
    print("🚀 ZombieCoder Local AI Framework - Test Runner")
    print("="*50)
    print("This will:")
    print("1. Stop existing processes")
    print("2. Start server with uvicorn")
    print("3. Check authentication")
    print("4. Load models")
    print("5. Run API tests")
    print("6. Run chat tests")
    print("7. Show real-time status")
    print("8. Export JSON results")
    print("="*50)
    
    response = input("\nDo you want to continue? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        print("\n🔄 Starting automated test suite...")
        try:
            # Run the complete test
            result = subprocess.run([sys.executable, 'complete_automated_test.py'], 
                                 capture_output=False, text=True)
            
            if result.returncode == 0:
                print("\n✅ Test suite completed successfully!")
            else:
                print("\n❌ Test suite failed!")
                
        except Exception as e:
            print(f"\n❌ Error running test suite: {e}")
    else:
        print("\n❌ Test cancelled by user.")

if __name__ == "__main__":
    main()
