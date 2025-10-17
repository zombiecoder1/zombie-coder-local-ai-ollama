#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Summary Printer - সুন্দরভাবে টেস্ট রেজাল্ট দেখায়
"""

import json
from pathlib import Path

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
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def main():
    report_file = Path(__file__).parent / "test_report.json"
    
    if not report_file.exists():
        print("Test report not found. Run tests first: python run_all_tests.py")
        return
    
    with open(report_file, encoding="utf-8") as f:
        report = json.load(f)
    
    print_header("ZombieCoder Local AI - Test Results")
    
    print(f"{Colors.BOLD}Timestamp:{Colors.END} {report['timestamp']}")
    print(f"{Colors.BOLD}Total Tests:{Colors.END} {report['total']}")
    print(f"{Colors.GREEN}{Colors.BOLD}Passed:{Colors.END} {report['passed']}")
    print(f"{Colors.RED}{Colors.BOLD}Failed:{Colors.END} {report['failed']}")
    print(f"{Colors.BOLD}Duration:{Colors.END} {report['duration']:.1f}s")
    
    success_rate = (report['passed'] / report['total'] * 100) if report['total'] > 0 else 0
    color = Colors.GREEN if success_rate == 100 else (Colors.YELLOW if success_rate >= 80 else Colors.RED)
    print(f"\n{Colors.BOLD}Success Rate:{Colors.END} {color}{success_rate:.1f}%{Colors.END}")
    
    print(f"\n{Colors.BOLD}Individual Test Results:{Colors.END}\n")
    
    for test in report['tests']:
        name = test['name']
        success = test['success']
        duration = test.get('duration', 0)
        
        status = f"{Colors.GREEN}PASS{Colors.END}" if success else f"{Colors.RED}FAIL{Colors.END}"
        icon = "✓" if success else "✗"
        
        print(f"  {icon} {status} - {name:<30} ({duration:.1f}s)")
    
    print()
    
    # Show core tests specifically
    core_tests = [t for t in report['tests'] if t['name'].startswith(('01_', '02_', '03_', '04_', '05_'))]
    core_passed = sum(1 for t in core_tests if t['success'])
    
    print(f"{Colors.BOLD}Core Tests (01-05):{Colors.END} {core_passed}/{len(core_tests)} passed")
    
    if core_passed == len(core_tests):
        print_header("All Core Tests PASSED! System is READY!")
    else:
        print_header(f"Warning: {len(core_tests) - core_passed} Core Tests Failed")
    
    # Show model info from first test
    first_test = report['tests'][0] if report['tests'] else {}
    if 'output' in first_test:
        try:
            output = json.loads(first_test['output'])
            if 'checks' in output and 'installed' in output['checks']:
                installed = output['checks']['installed']
                models = installed.get('models', [])
                
                print(f"\n{Colors.BOLD}Installed Models:{Colors.END}")
                for m in models:
                    name = m.get('name', 'Unknown')
                    size = m.get('size_mb', 0)
                    print(f"  - {name}: {size:.1f} MB")
                
                has_gguf = output['checks'].get('has_gguf_model', False)
                if has_gguf:
                    print(f"\n{Colors.GREEN}GGUF model detected - inference ready!{Colors.END}")
        except:
            pass
    
    print()

if __name__ == "__main__":
    main()

