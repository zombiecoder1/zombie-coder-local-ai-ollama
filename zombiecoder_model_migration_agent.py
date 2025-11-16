#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder Model Migration Agent v1.0
Fully automated model directory scanning, analysis, and migration assistant
"""

import os
import json
import sys
import requests
import time
from pathlib import Path
from typing import List, Dict, Any

class ZombieCoderMigrationAgent:
    def __init__(self):
        """Initialize the agent with automatic directory detection"""
        self.base_dir = Path.cwd()
        self.models_dir = self._detect_models_directory()
        self.found_models = []
        self.incompatible_models = []
        self.low_power_models = []
        self.working_models = []
        self.safe_to_delete = []
        self.recommended_model = None
        self.api_base_url = "http://localhost:8007"
        self.final_report = {}
        
    def _detect_models_directory(self) -> Path:
        """Step 1: Automatically detect models directory"""
        print("🔍 Auto-detecting models directory...")
        
        # Check common locations
        possible_paths = [
            self.base_dir / "models",
            self.base_dir / "Models",
            Path.home() / "models",
            Path.home() / "Models"
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                print(f"✅ Found models directory at: {path}")
                return path
        
        # If not found, create in current directory
        default_path = self.base_dir / "models"
        print(f"📁 Creating models directory at: {default_path}")
        default_path.mkdir(exist_ok=True)
        return default_path
    
    def scan_model_directories(self) -> Dict[str, Any]:
        """Step 1-3: Scan directories and classify models"""
        print("\n🔍 Scanning model directories...")
        
        if not self.models_dir.exists():
            print(f"❌ Models directory not found at {self.models_dir}")
            return {}
        
        # Scan all subdirectories in models folder
        for item in self.models_dir.iterdir():
            if item.is_dir():
                model_info = self._analyze_model_directory(item)
                if model_info:
                    self.found_models.append(model_info)
        
        # Classify models
        self._classify_models()
        
        inventory = {
            "detected_directory": str(self.models_dir),
            "total_models_found": len(self.found_models),
            "model_details": self.found_models,
            "incompatible": self.incompatible_models,
            "low_power": self.low_power_models,
            "working": self.working_models,
            "safe_to_delete": self.safe_to_delete
        }
        
        print(f"📊 Scan complete: {len(self.found_models)} models found")
        return inventory
    
    def _analyze_model_directory(self, model_dir: Path) -> Dict[str, Any]:
        """Analyze a single model directory"""
        model_info = {
            "name": model_dir.name,
            "path": str(model_dir),
            "gguf_files": [],
            "safetensors_files": [],
            "size_mb": 0,
            "format": "unknown",
            "parameters": "unknown"
        }
        
        # Check for GGUF files
        gguf_files = list(model_dir.glob("*.gguf"))
        model_info["gguf_files"] = [str(f.name) for f in gguf_files]
        
        # Check for safetensors files
        safetensors_files = list(model_dir.glob("*.safetensors"))
        model_info["safetensors_files"] = [str(f.name) for f in safetensors_files]
        
        # Calculate total size
        total_size = 0
        for file in model_dir.rglob("*"):
            if file.is_file():
                total_size += file.stat().st_size
        
        model_info["size_mb"] = round(total_size / (1024 * 1024), 2)
        
        # Determine format and estimate parameters
        if gguf_files:
            model_info["format"] = "gguf"
            # Estimate parameters based on file size (rough approximation)
            if total_size < 500 * 1024 * 1024:  # < 500MB
                model_info["parameters"] = "<1B"
            elif total_size < 2 * 1024 * 1024 * 1024:  # < 2GB
                model_info["parameters"] = "1B-3B"
            elif total_size < 5 * 1024 * 1024 * 1024:  # < 5GB
                model_info["parameters"] = "3B-7B"
            else:
                model_info["parameters"] = ">7B"
        elif safetensors_files:
            model_info["format"] = "safetensors"
            model_info["parameters"] = "unknown"
        else:
            model_info["format"] = "unknown"
            model_info["parameters"] = "unknown"
        
        return model_info
    
    def _classify_models(self):
        """Classify models based on format and capabilities"""
        for model in self.found_models:
            # Incompatible models (safetensors format)
            if model["format"] == "safetensors":
                self.incompatible_models.append(model["name"])
                self.safe_to_delete.append(model["name"])
            
            # Low power models (<1B parameters)
            elif model["parameters"] == "<1B":
                self.low_power_models.append(model["name"])
                self.safe_to_delete.append(model["name"])
            
            # Working models (GGUF format with sufficient parameters)
            elif model["format"] == "gguf":
                self.working_models.append(model["name"])
    
    def recommend_new_model(self) -> Dict[str, Any]:
        """Step 4: Recommend new model with download command"""
        print("\n💡 Recommending new model...")
        
        # Determine save location
        target_dir = self.models_dir / "qwen2.5-7b-instruct-gguf"
        
        recommendation = {
            "model_name": "Qwen2.5-7B-Instruct-GGUF",
            "preferred_quantization": "Q4_K_M",
            "size_estimate_gb": "4.5-6",
            "target_save_location": str(target_dir),
            "download_command": f"huggingface-cli download Qwen/Qwen2.5-7B-Instruct-GGUF --local-dir \"{target_dir}\" --local-dir-use-symlinks False"
        }
        
        self.recommended_model = recommendation
        return recommendation
    
    def suggest_config_updates(self) -> Dict[str, Any]:
        """Step 5: Suggest configuration updates"""
        print("\n⚙️  Suggesting configuration updates...")
        
        # Find the recommended model path
        model_path = ""
        if self.recommended_model:
            model_path = f"{self.recommended_model['target_save_location']}/qwen2.5-7b-instruct-q4_k_m.gguf"
        
        config_suggestion = {
            "model_path": model_path,
            "context_length": 4096,
            "gpu_layers": "auto",
            "lazy_load": True,
            "low_vram": True
        }
        
        return config_suggestion
    
    def run_capability_tests(self, model_name: str = "qwen2.5-0.5b-instruct-gguf") -> Dict[str, str]:
        """Step 6-7: Run capability tests and generate results"""
        print(f"\n🧪 Running capability tests on {model_name}...")
        
        test_results = {
            "bangla_test": "pending",
            "json_test": "pending",
            "code_test": "pending"
        }
        
        try:
            # Test 1: Bangla Response
            print("  Testing Bangla language support...")
            bangla_prompt = "বাংলায় ২ লাইনের সারাংশ লিখুন: আজ আকাশে অনেক মেঘ।"
            bangla_result = self._test_model_prompt(model_name, bangla_prompt)
            test_results["bangla_test"] = "ok" if bangla_result and len(bangla_result) > 10 else "failed"
            
            # Test 2: JSON Validation
            print("  Testing JSON generation...")
            json_prompt = "Return ONLY valid JSON. Create a todo list with 3 items."
            json_result = self._test_model_prompt(model_name, json_prompt)
            test_results["json_test"] = "valid" if json_result and self._is_valid_json(json_result) else "invalid"
            
            # Test 3: Code Generation
            print("  Testing code generation...")
            code_prompt = "Write a python function that returns fib(10). Only return the function, no explanation."
            code_result = self._test_model_prompt(model_name, code_prompt)
            test_results["code_test"] = "passed" if code_result and "def" in code_result and "fib" in code_result else "failed"
            
        except Exception as e:
            print(f"  ❌ Test error: {e}")
            test_results["error"] = str(e)
        
        return test_results
    
    def _test_model_prompt(self, model_name: str, prompt: str) -> str:
        """Test a model with a specific prompt"""
        try:
            data = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "max_tokens": 150
            }
            
            response = requests.post(
                f"{self.api_base_url}/api/generate",
                headers={"Content-Type": "application/json"},
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("runtime_response", {}).get("content", "")
                return content.strip()
            else:
                print(f"    HTTP {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"    Request error: {e}")
            return ""
    
    def _is_valid_json(self, text: str) -> bool:
        """Check if text is valid JSON"""
        try:
            # Try to parse as JSON
            parsed = json.loads(text)
            # Check if it's a dict or list (valid JSON structures)
            return isinstance(parsed, (dict, list))
        except json.JSONDecodeError:
            return False
    
    def prepare_cleanup_plan(self) -> Dict[str, List[str]]:
        """Step 8: Prepare cleanup plan"""
        print("\n🗑️  Preparing cleanup plan...")
        
        return {
            "safe_to_delete": self.safe_to_delete
        }
    
    def generate_final_report(self, inventory: Dict, recommendation: Dict, 
                            config_updates: Dict, test_results: Dict, 
                            cleanup_plan: Dict) -> Dict[str, Any]:
        """Step 9: Generate final consolidated report"""
        print("\n📋 Generating final report...")
        
        self.final_report = {
            "agent_version": "ZombieCoder Model Migration Agent v1.0",
            "scan_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "detected_directory": inventory.get("detected_directory", ""),
            "model_inventory": {
                "total_models_found": inventory.get("total_models_found", 0),
                "model_details": inventory.get("model_details", []),
                "classification": {
                    "incompatible": inventory.get("incompatible", []),
                    "low_power": inventory.get("low_power", []),
                    "working": inventory.get("working", [])
                }
            },
            "recommended_model": recommendation,
            "config_updates": config_updates,
            "test_results": test_results,
            "cleanup_plan": cleanup_plan,
            "migration_status": "analysis_complete"
        }
        
        # Save report
        report_file = self.base_dir / "zombiecoder_migration_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.final_report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Final report saved to: {report_file}")
        return self.final_report
    
    def display_summary(self):
        """Display a summary of the migration plan"""
        if not self.final_report:
            print("❌ No report available")
            return
        
        print("\n" + "="*60)
        print("ZOMBIECODER MODEL MIGRATION SUMMARY")
        print("="*60)
        print(f"📍 Models Directory: {self.final_report.get('detected_directory', 'N/A')}")
        print(f"📊 Models Found: {self.final_report['model_inventory']['total_models_found']}")
        print(f"⚠️  Incompatible Models: {len(self.final_report['model_inventory']['classification']['incompatible'])}")
        print(f"📉 Low-Power Models: {len(self.final_report['model_inventory']['classification']['low_power'])}")
        print(f"✅ Working Models: {len(self.final_report['model_inventory']['classification']['working'])}")
        print(f"📥 Recommended Model: {self.final_report['recommended_model']['model_name']}")
        print(f"🗑️  Safe to Delete: {len(self.final_report['cleanup_plan']['safe_to_delete'])}")
        
        if "test_results" in self.final_report:
            print("\n🧪 Test Results:")
            tests = self.final_report["test_results"]
            print(f"  Bangla Test: {tests.get('bangla_test', 'N/A')}")
            print(f"  JSON Test: {tests.get('json_test', 'N/A')}")
            print(f"  Code Test: {tests.get('code_test', 'N/A')}")
        
        print("\n📋 Next Steps:")
        print("  1. Review the detailed report in zombiecoder_migration_report.json")
        print("  2. Run the download command to install the recommended model")
        print("  3. Apply configuration updates after installation")
        print("  4. Run tests to verify new model functionality")
        print("  5. Approve cleanup plan to remove old models")
        
        print("\n⚠️  IMPORTANT: No changes have been applied automatically.")
        print("   Please review and approve before proceeding with any actions.")
    
    def execute_migration_process(self):
        """Main execution function - follows all 10 steps exactly"""
        print("🤖 ZombieCoder Model Migration Agent v1.0")
        print("=" * 50)
        
        # Step 1-3: Scan and classify models
        inventory = self.scan_model_directories()
        
        # Step 4: Recommend new model
        recommendation = self.recommend_new_model()
        
        # Step 5: Suggest config updates
        config_updates = self.suggest_config_updates()
        
        # Step 6-7: Run tests and generate results
        # Using existing working model for tests
        working_model = self.working_models[0] if self.working_models else "qwen2.5-0.5b-instruct-gguf"
        test_results = self.run_capability_tests(working_model)
        
        # Step 8: Prepare cleanup plan
        cleanup_plan = self.prepare_cleanup_plan()
        
        # Step 9: Generate final report
        final_report = self.generate_final_report(
            inventory, recommendation, config_updates, test_results, cleanup_plan
        )
        
        # Step 10: Display summary and wait for user approval
        self.display_summary()
        
        return final_report

if __name__ == "__main__":
    agent = ZombieCoderMigrationAgent()
    agent.execute_migration_process()