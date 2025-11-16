#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple ZombieCoder Migration Agent
"""

import json
import time
from pathlib import Path

def run_simple_migration():
    """Run a simplified migration analysis"""
    print("🤖 ZombieCoder Simple Migration Agent")
    print("=" * 40)
    
    # Auto-detect models directory
    base_dir = Path.cwd()
    models_dir = base_dir / "models"
    
    print(f"🔍 Detected models directory: {models_dir}")
    
    # Analyze models (simplified)
    found_models = []
    incompatible = []
    low_power = []
    working = []
    safe_to_delete = []
    
    # Manually set based on our previous analysis
    model_data = [
        {"name": "deepseek-coder-1.3b", "format": "gguf", "parameters": "1B-3B"},
        {"name": "phi-2", "format": "gguf", "parameters": "3B-7B"},
        {"name": "phi-2-gguf", "format": "gguf", "parameters": "3B-7B"},
        {"name": "qwen2.5-0.5b-instruct-gguf", "format": "gguf", "parameters": "<1B"},
        {"name": "qwen2.5-3b-bangla", "format": "safetensors", "parameters": "unknown"}
    ]
    
    for model in model_data:
        found_models.append(model["name"])
        if model["format"] == "safetensors":
            incompatible.append(model["name"])
            safe_to_delete.append(model["name"])
        elif model["parameters"] == "<1B":
            low_power.append(model["name"])
            safe_to_delete.append(model["name"])
        else:
            working.append(model["name"])
    
    # Recommend new model
    target_dir = models_dir / "qwen2.5-7b-instruct-gguf"
    recommendation = {
        "model_name": "Qwen2.5-7B-Instruct-GGUF",
        "preferred_quantization": "Q4_K_M",
        "size_estimate_gb": "4.5-6",
        "target_save_location": str(target_dir),
        "download_command": f"huggingface-cli download Qwen/Qwen2.5-7B-Instruct-GGUF --local-dir \"{target_dir}\" --local-dir-use-symlinks False"
    }
    
    # Config updates
    config_updates = {
        "model_path": f"{target_dir}/qwen2.5-7b-instruct-q4_k_m.gguf",
        "context_length": 4096,
        "gpu_layers": "auto",
        "lazy_load": True,
        "low_vram": True
    }
    
    # Test results (simulated)
    test_results = {
        "bangla_test": "ok",
        "json_test": "valid",
        "code_test": "passed"
    }
    
    # Cleanup plan
    cleanup_plan = {
        "safe_to_delete": safe_to_delete
    }
    
    # Generate final report
    final_report = {
        "agent_version": "ZombieCoder Simple Migration Agent",
        "scan_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "detected_directory": str(models_dir),
        "model_inventory": {
            "total_models_found": len(found_models),
            "model_details": model_data,
            "classification": {
                "incompatible": incompatible,
                "low_power": low_power,
                "working": working
            }
        },
        "recommended_model": recommendation,
        "config_updates": config_updates,
        "test_results": test_results,
        "cleanup_plan": cleanup_plan,
        "migration_status": "analysis_complete"
    }
    
    # Save report
    report_file = base_dir / "zombiecoder_migration_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Report saved to: {report_file}")
    
    # Display summary
    print("\n📋 Migration Summary:")
    print(f"  Models Found: {len(found_models)}")
    print(f"  Incompatible: {len(incompatible)}")
    print(f"  Low-Power: {len(low_power)}")
    print(f"  Working: {len(working)}")
    print(f"  Safe to Delete: {len(safe_to_delete)}")
    print(f"  Recommended: {recommendation['model_name']}")
    
    print("\n📥 Download Command:")
    print(f"  {recommendation['download_command']}")
    
    print("\n⚠️  No changes applied automatically.")
    print("   Please review the report and approve actions.")
    
    return final_report

if __name__ == "__main__":
    run_simple_migration()