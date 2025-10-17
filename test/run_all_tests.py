#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
সব টেস্ট চালানোর Master Script
সব টেস্ট স্ক্রিপ্ট এক এক করে চালায় এবং রিপোর্ট তৈরি করে
"""

import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def run_test(test_file: Path, timeout: int = 60) -> dict:
    """একটি টেস্ট স্ক্রিপ্ট চালায়"""
    test_name = test_file.stem
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}► টেস্ট চলছে: {test_name}{Colors.END}")
    print(f"  ফাইল: {test_file.name}")
    
    result = {
        "name": test_name,
        "file": test_file.name,
        "start_time": datetime.now().isoformat(),
        "success": False,
        "duration": 0,
        "output": "",
        "error": ""
    }
    
    try:
        start_time = time.time()
        
        # চালান
        process = subprocess.run(
            ["python", str(test_file)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=test_file.parent
        )
        
        result["duration"] = time.time() - start_time
        result["output"] = process.stdout
        result["error"] = process.stderr
        result["returncode"] = process.returncode
        
        if process.returncode == 0:
            result["success"] = True
            print_success(f"পাস! সময়: {result['duration']:.1f}s")
        else:
            print_error(f"ব্যর্থ! (exitcode: {process.returncode})")
            if process.stderr:
                print(f"{Colors.RED}{process.stderr[:500]}{Colors.END}")
        
    except subprocess.TimeoutExpired:
        result["duration"] = timeout
        result["error"] = f"Timeout after {timeout}s"
        print_error(f"টাইমআউট! ({timeout}s)")
    except Exception as e:
        result["error"] = str(e)
        print_error(f"এরর: {str(e)}")
    
    result["end_time"] = datetime.now().isoformat()
    return result

def main():
    print_header("ZombieCoder Local AI - সম্পূর্ণ টেস্ট স্যুট")
    print_info(f"সময়: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_dir = Path(__file__).parent
    
    # টেস্ট ফাইল তালিকা (ক্রমানুসারে)
    test_files = sorted([
        f for f in test_dir.glob("*.py")
        if f.name.startswith(("01_", "02_", "03_", "04_", "05_", "06_", "07_"))
        and f.name != "run_all_tests.py"
    ])
    
    if not test_files:
        print_error("কোনো টেস্ট ফাইল পাওয়া যায়নি!")
        return
    
    print_info(f"মোট {len(test_files)} টেস্ট পাওয়া গেছে")
    for tf in test_files:
        print(f"  - {tf.name}")
    
    # সব টেস্ট চালান
    results = []
    passed = 0
    failed = 0
    
    start_time = time.time()
    
    for i, test_file in enumerate(test_files, 1):
        print(f"\n{Colors.BOLD}[{i}/{len(test_files)}]{Colors.END}")
        
        # Set timeout based on test
        timeout = 60
        if "lifecycle" in test_file.name or "gguf" in test_file.name:
            timeout = 120  # Model loading tests need more time
        
        result = run_test(test_file, timeout=timeout)
        results.append(result)
        
        if result["success"]:
            passed += 1
        else:
            failed += 1
        
        # Wait a bit between tests
        if i < len(test_files):
            time.sleep(2)
    
    total_duration = time.time() - start_time
    
    # সারসংক্ষেপ
    print_header("টেস্ট রিপোর্ট - সারসংক্ষেপ")
    
    print(f"\n{Colors.BOLD}সামগ্রিক ফলাফল:{Colors.END}")
    print(f"  মোট টেস্ট: {len(results)}")
    print(f"  {Colors.GREEN}✓ পাস: {passed}{Colors.END}")
    print(f"  {Colors.RED}✗ ফেইল: {failed}{Colors.END}")
    print(f"  মোট সময়: {total_duration:.1f}s")
    
    print(f"\n{Colors.BOLD}টেস্ট বিবরণ:{Colors.END}")
    for result in results:
        status = f"{Colors.GREEN}✓ পাস{Colors.END}" if result["success"] else f"{Colors.RED}✗ ফেইল{Colors.END}"
        duration = result.get("duration", 0)
        print(f"  {status} - {result['name']} ({duration:.1f}s)")
    
    # JSON রিপোর্ট সংরক্ষণ
    report_file = test_dir / "test_report.json"
    report = {
        "timestamp": datetime.now().isoformat(),
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "duration": total_duration,
        "tests": results
    }
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print_info(f"\nবিস্তারিত রিপোর্ট সংরক্ষিত: {report_file}")
    
    # সফলতার হার
    success_rate = (passed / len(results) * 100) if results else 0
    print(f"\n{Colors.BOLD}সফলতার হার: {success_rate:.1f}%{Colors.END}")
    
    if failed == 0:
        print_header("🎉 সব টেস্ট সফল! 🎉")
    else:
        print_header(f"⚠ {failed} টেস্ট ব্যর্থ হয়েছে")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())

