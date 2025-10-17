#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
শুধুমাত্র Core Tests চালায় (01-05)
"""

import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def run_test(test_file: Path, timeout: int = 60) -> dict:
    """একটি টেস্ট চালায়"""
    test_name = test_file.stem
    print(f"\n{Colors.BOLD}Testing: {test_name}{Colors.END}")
    
    result = {
        "name": test_name,
        "file": test_file.name,
        "start_time": datetime.now().isoformat(),
        "success": False,
        "duration": 0
    }
    
    try:
        start_time = time.time()
        process = subprocess.run(
            ["python", str(test_file)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=test_file.parent
        )
        
        result["duration"] = time.time() - start_time
        result["returncode"] = process.returncode
        
        if process.returncode == 0:
            result["success"] = True
            print(f"{Colors.GREEN}✓ PASS{Colors.END} ({result['duration']:.1f}s)")
        else:
            print(f"{Colors.RED}✗ FAIL{Colors.END} (exitcode: {process.returncode})")
        
    except subprocess.TimeoutExpired:
        result["duration"] = timeout
        print(f"{Colors.RED}✗ TIMEOUT{Colors.END} ({timeout}s)")
    except Exception as e:
        print(f"{Colors.RED}✗ ERROR: {str(e)}{Colors.END}")
    
    result["end_time"] = datetime.now().isoformat()
    return result

def main():
    print_header("ZombieCoder Local AI - Core Tests (01-05)")
    
    test_dir = Path(__file__).parent
    
    # Core test files
    core_tests = [
        test_dir / "01_preflight_check.py",
        test_dir / "02_model_lifecycle.py",
        test_dir / "03_api_standard_check.py",
        test_dir / "04_ui_data_integrity.py",
        test_dir / "05_integrated_session_test.py",
    ]
    
    # Verify all exist
    for test_file in core_tests:
        if not test_file.exists():
            print(f"{Colors.RED}ERROR: {test_file.name} not found{Colors.END}")
            return 1
    
    # Run tests
    results = []
    passed = 0
    failed = 0
    
    start_time = time.time()
    
    for i, test_file in enumerate(core_tests, 1):
        print(f"\n{Colors.BOLD}[{i}/{len(core_tests)}]{Colors.END}")
        
        # Set timeout based on test
        timeout = 120 if "lifecycle" in test_file.name or "session" in test_file.name else 60
        
        result = run_test(test_file, timeout=timeout)
        results.append(result)
        
        if result["success"]:
            passed += 1
        else:
            failed += 1
        
        time.sleep(1)
    
    total_duration = time.time() - start_time
    
    # Summary
    print_header("Core Tests Summary")
    
    print(f"{Colors.BOLD}Results:{Colors.END}")
    print(f"  Total: {len(results)}")
    print(f"  {Colors.GREEN}✓ Passed: {passed}{Colors.END}")
    print(f"  {Colors.RED}✗ Failed: {failed}{Colors.END}")
    print(f"  Duration: {total_duration:.1f}s")
    
    success_rate = (passed / len(results) * 100) if results else 0
    
    print(f"\n{Colors.BOLD}Individual Results:{Colors.END}")
    for result in results:
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if result["success"] else f"{Colors.RED}✗ FAIL{Colors.END}"
        duration = result.get("duration", 0)
        print(f"  {status} - {result['name']:<30} ({duration:.1f}s)")
    
    print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.END}")
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_type": "core_tests",
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "duration": total_duration,
        "success_rate": success_rate,
        "tests": results
    }
    
    report_file = test_dir / "core_test_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n{Colors.BLUE}Report saved: {report_file}{Colors.END}")
    
    if failed == 0:
        print_header("ALL CORE TESTS PASSED! ✓")
        return 0
    else:
        print_header(f"{failed} CORE TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    exit(main())

