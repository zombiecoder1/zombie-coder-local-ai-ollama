#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Migration Plan Generator
"""

import json
import requests
from pathlib import Path

def generate_final_migration_plan():
    """Generate the final migration plan based on our analysis"""
    
    # Migration plan based on our findings
    migration_plan = {
        "model_migration_plan": {
            "current_status": {
                "found_models": 6,
                "incompatible_models": ["qwen2.5-3b-bangla"],
                "low_power_models": ["qwen2.5-0.5b-instruct-gguf"],
                "working_models": ["phi-2", "phi-2-gguf", "deepseek-coder-1.3b"]
            },
            "recommended_action": {
                "install_new_model": {
                    "model_name": "Qwen2.5-7B-Instruct-GGUF",
                    "quantization": "Q4_K_M",
                    "reason": "Better balance of capability and resource usage for Bangla language support",
                    "estimated_size_gb": "4.5-6",
                    "download_command": "huggingface-cli download Qwen/Qwen2.5-7B-Instruct-GGUF --local-dir models/qwen2.5-7b-instruct-gguf --local-dir-use-symlinks False"
                },
                "safe_to_delete": [
                    "qwen2.5-3b-bangla",  # Incompatible safetensors format
                    "qwen2.5-0.5b-instruct-gguf"  # Low capability model
                ],
                "keep_models": [
                    "phi-2",  # Working model
                    "phi-2-gguf",  # Working model
                    "deepseek-coder-1.3b"  # Working model
                ]
            },
            "config_updates": {
                "new_model_config": {
                    "model_path": "models/qwen2.5-7b-instruct-gguf/qwen2.5-7b-instruct-q4_k_m.gguf",
                    "context_length": 4096,
                    "gpu_layers": "auto",
                    "lazy_load": True,
                    "low_vram": True
                }
            },
            "testing_plan": {
                "test_cases": [
                    {
                        "name": "Bangla Language Support",
                        "prompt": "বাংলায় ২ লাইনের সারাংশ লিখুন: আজ আকাশে অনেক মেঘ।",
                        "expected": "Response in Bangla language"
                    },
                    {
                        "name": "JSON Generation",
                        "prompt": "Return ONLY valid JSON. Create a todo list with 3 items.",
                        "expected": "Valid JSON format"
                    },
                    {
                        "name": "Code Generation",
                        "prompt": "Write a python function that returns fib(10). Only return the function, no explanation.",
                        "expected": "Valid Python function"
                    }
                ]
            },
            "implementation_steps": [
                "1. Download Qwen2.5-7B-Instruct-GGUF using the provided command",
                "2. Verify the model loads correctly with lazy loading",
                "3. Test all three test cases to validate functionality",
                "4. Update configuration to use the new model as default",
                "5. Remove the safe_to_delete models to free disk space",
                "6. Document the migration in the model registry"
            ]
        }
    }
    
    # Save the migration plan
    plan_file = Path("model_migration_plan.json")
    with open(plan_file, "w", encoding="utf-8") as f:
        json.dump(migration_plan, f, indent=2, ensure_ascii=False)
    
    print("✅ Final migration plan generated!")
    print(f"📋 Plan saved to: {plan_file}")
    
    # Print summary
    print("\n📋 Migration Plan Summary:")
    print(f"  🔧 Models to install: 1")
    print(f"  🗑️  Models to delete: {len(migration_plan['model_migration_plan']['recommended_action']['safe_to_delete'])}")
    print(f"  💾 Models to keep: {len(migration_plan['model_migration_plan']['recommended_action']['keep_models'])}")
    print(f"  🧪 Test cases: {len(migration_plan['model_migration_plan']['testing_plan']['test_cases'])}")
    
    return migration_plan

if __name__ == "__main__":
    generate_final_migration_plan()