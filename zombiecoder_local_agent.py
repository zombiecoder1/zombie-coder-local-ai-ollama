#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder Local Model Agent
Follows explicit instructions for safe and clear model management
"""

import os
import sys
import json
import shutil
import psutil
import requests
import subprocess
from pathlib import Path
from typing import List, Dict, Any

class ZombieCoderLocalAgent:
    def __init__(self):
        """Initialize the agent with automatic directory detection"""
        self.base_dir = Path.cwd()
        self.models_dir = self._detect_models_directory()
        self.lock_fix_mode = False
        self.report = {
            "agent_version": "ZombieCoder Local Model Agent v1.0",
            "execution_timestamp": "",
            "models_directory": str(self.models_dir),
            "lock_status": {},
            "deleted_models": [],
            "downloaded_models": [],
            "test_results": {},
            "config_updates": {},
            "migration_summary": {}
        }
    
    def _detect_models_directory(self) -> Path:
        """Step 1: Auto-detect models directory"""
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
    
    def fix_lock_files(self) -> Dict[str, Any]:
        """Step 1: Release old locks"""
        print("\n🔧 Fixing lock files...")
        lock_status = {
            "lock_files_found": [],
            "lock_files_deleted": [],
            "processes_holding_locks": []
        }
        
        cache_dir = self.models_dir / ".cache" / "huggingface" / "download"
        if cache_dir.exists():
            # Find all .lock files
            lock_files = list(cache_dir.glob("*.lock"))
            lock_status["lock_files_found"] = [str(f) for f in lock_files]
            
            if lock_files:
                print(f"Found {len(lock_files)} lock files")
                
                for lock_file in lock_files:
                    # Check if any process is holding this file
                    holding_processes = []
                    for proc in psutil.process_iter(['pid', 'name', 'open_files']):
                        try:
                            if proc.info['open_files']:
                                for open_file in proc.info['open_files']:
                                    if lock_file.name in open_file.path:
                                        holding_processes.append({
                                            "pid": proc.info['pid'],
                                            "name": proc.info['name'],
                                            "file": open_file.path
                                        })
                        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                            pass
                    
                    if holding_processes:
                        print(f"⚠️  Process holding lock {lock_file.name}: {holding_processes}")
                        lock_status["processes_holding_locks"].extend(holding_processes)
                    else:
                        # Safe to delete
                        try:
                            lock_file.unlink()
                            print(f"✅ Deleted lock file: {lock_file.name}")
                            lock_status["lock_files_deleted"].append(str(lock_file))
                        except Exception as e:
                            print(f"❌ Error deleting lock file {lock_file.name}: {e}")
            else:
                print("✅ No lock files found")
        else:
            print("✅ No cache directory found")
        
        self.report["lock_status"] = lock_status
        return lock_status
    
    def identify_safe_delete_models(self) -> List[str]:
        """Step 2: Identify models safe to delete"""
        print("\n🧹 Identifying models safe to delete...")
        safe_to_delete = []
        
        # Models to delete based on previous analysis
        models_to_delete = [
            "qwen2.5-3b-bangla",        # safetensors → incompatible
            "qwen2.5-0.5b-instruct-gguf"  # low-power, not required
        ]
        
        for model_name in models_to_delete:
            model_path = self.models_dir / model_name
            if model_path.exists():
                safe_to_delete.append(model_name)
                print(f"✅ Marked for deletion: {model_name}")
            else:
                print(f"⚠️  Model not found: {model_name}")
        
        print(f"\nSafe to delete list: {safe_to_delete}")
        return safe_to_delete
    
    def delete_models(self, model_list: List[str]) -> Dict[str, Any]:
        """Delete specified models"""
        print("\n🗑️  Deleting models...")
        deletion_report = {
            "attempted_deletions": model_list,
            "successfully_deleted": [],
            "failed_deletions": []
        }
        
        for model_name in model_list:
            model_path = self.models_dir / model_name
            if model_path.exists():
                try:
                    # Unload model if it's loaded
                    self._unload_model(model_name)
                    
                    # Delete the model
                    if model_path.is_dir():
                        shutil.rmtree(model_path)
                    else:
                        model_path.unlink()
                    
                    print(f"✅ Deleted: {model_name}")
                    deletion_report["successfully_deleted"].append(model_name)
                    self.report["deleted_models"].append(model_name)
                except Exception as e:
                    print(f"❌ Error deleting {model_name}: {e}")
                    deletion_report["failed_deletions"].append({"model": model_name, "error": str(e)})
            else:
                print(f"⚠️  Model not found: {model_name}")
        
        return deletion_report
    
    def _unload_model(self, model_name: str):
        """Unload a model from the runtime"""
        try:
            response = requests.post(
                f"http://localhost:8007/runtime/unload/{model_name}",
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ Unloaded model: {model_name}")
            else:
                print(f"⚠️  Could not unload model {model_name}: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Error unloading model {model_name}: {e}")
    
    def download_model(self, model_repo: str, model_file: str, target_dir: str) -> Dict[str, Any]:
        """Step 3: Download new model"""
        print(f"\n⚡ Downloading model: {model_file}")
        download_report = {
            "model_repo": model_repo,
            "model_file": model_file,
            "target_dir": target_dir,
            "status": "started",
            "error": None
        }
        
        # Create target directory
        target_path = self.models_dir / target_dir
        target_path.mkdir(exist_ok=True)
        
        # Activate virtual environment and download
        try:
            # Check if we're in virtual environment
            venv_active = 'VIRTUAL_ENV' in os.environ
            print(f"Virtual environment active: {venv_active}")
            
            # Construct download command
            cmd = [
                "hf", "download", model_repo,
                "--include", model_file,
                "--local-dir", str(target_path)
            ]
            
            print(f"Executing: {' '.join(cmd)}")
            
            # Run download command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                print("✅ Download completed successfully")
                download_report["status"] = "completed"
                self.report["downloaded_models"].append({
                    "repo": model_repo,
                    "file": model_file,
                    "path": str(target_path)
                })
            else:
                print(f"❌ Download failed: {result.stderr}")
                download_report["status"] = "failed"
                download_report["error"] = result.stderr
                
        except subprocess.TimeoutExpired:
            print("❌ Download timed out")
            download_report["status"] = "timeout"
        except Exception as e:
            print(f"❌ Download error: {e}")
            download_report["status"] = "error"
            download_report["error"] = str(e)
        
        return download_report
    
    def run_model_tests(self, model_name: str) -> Dict[str, Any]:
        """Step 4: Run tests on new model"""
        print(f"\n🧪 Running tests on model: {model_name}")
        test_results = {
            "model_name": model_name,
            "tests": {}
        }
        
        # Test 1: Bangla test
        print("  Running Bangla test...")
        bangla_result = self._run_test_prompt(
            model_name,
            "বাংলায় ১ লাইনের সারাংশ লিখো: আজ বৃষ্টি হচ্ছে।"
        )
        test_results["tests"]["bangla"] = bangla_result
        
        # Test 2: JSON test
        print("  Running JSON test...")
        json_result = self._run_test_prompt(
            model_name,
            "Return ONLY valid JSON: {a:1}"
        )
        test_results["tests"]["json"] = json_result
        
        # Test 3: Code generation test
        print("  Running code generation test...")
        code_result = self._run_test_prompt(
            model_name,
            "Write a python function that returns fib(10). Only code."
        )
        test_results["tests"]["code"] = code_result
        
        self.report["test_results"] = test_results
        return test_results
    
    def _run_test_prompt(self, model_name: str, prompt: str) -> Dict[str, Any]:
        """Run a single test prompt"""
        test_result = {
            "prompt": prompt,
            "response": "",
            "status": "pending",
            "error": None
        }
        
        try:
            data = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "max_tokens": 150,
                "context_length": 4096,
                "gpu_layers": "auto",
                "lazy_load": True
            }
            
            response = requests.post(
                "http://localhost:8007/api/generate",
                headers={"Content-Type": "application/json"},
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("runtime_response", {}).get("content", "")
                test_result["response"] = content
                test_result["status"] = "success"
            else:
                test_result["status"] = "failed"
                test_result["error"] = f"HTTP {response.status_code}"
                
        except Exception as e:
            test_result["status"] = "error"
            test_result["error"] = str(e)
        
        return test_result
    
    def update_configurations(self, model_path: str) -> Dict[str, Any]:
        """Step 5: Update configurations"""
        print(f"\n🔄 Updating configurations for: {model_path}")
        config_updates = {
            "files_updated": [],
            "files_not_found": [],
            "errors": []
        }
        
        # Configuration template
        config_template = {
            "model_path": model_path,
            "context_length": 4096,
            "gpu_layers": "auto",
            "lazy_load": True,
            "low_vram": True
        }
        
        # Files to update
        config_files = [
            "model_server.py",
            "agent_config.json",
            "zombiecoder.json"
        ]
        
        for config_file in config_files:
            file_path = self.base_dir / config_file
            if file_path.exists():
                try:
                    # For JSON files, update the model_path
                    if config_file.endswith(".json"):
                        with open(file_path, "r", encoding="utf-8") as f:
                            config_data = json.load(f)
                        
                        # Update model_path
                        config_data["model_path"] = model_path
                        
                        # Write back
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(config_data, f, indent=2, ensure_ascii=False)
                        
                        print(f"✅ Updated {config_file}")
                        config_updates["files_updated"].append(config_file)
                    else:
                        # For Python files, we would need to find and replace
                        # This is a simplified approach - in reality, you'd want more sophisticated parsing
                        print(f"⚠️  Python file update not implemented: {config_file}")
                        config_updates["files_not_found"].append(config_file)
                        
                except Exception as e:
                    print(f"❌ Error updating {config_file}: {e}")
                    config_updates["errors"].append({"file": config_file, "error": str(e)})
            else:
                print(f"⚠️  Config file not found: {config_file}")
                config_updates["files_not_found"].append(config_file)
        
        self.report["config_updates"] = config_updates
        return config_updates
    
    def generate_migration_summary(self) -> Dict[str, Any]:
        """Step 6: Generate migration summary"""
        print("\n📦 Generating migration summary...")
        
        # Create JSON report
        json_report_path = self.base_dir / "model_migration_report.json"
        with open(json_report_path, "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        # Create Markdown summary
        md_report_path = self.base_dir / "MODEL_MIGRATION_SUMMARY.md"
        with open(md_report_path, "w", encoding="utf-8") as f:
            f.write("# ZombieCoder Model Migration Summary\n\n")
            f.write(f"**Agent Version**: {self.report['agent_version']}\n\n")
            f.write(f"**Execution Time**: {self.report.get('execution_timestamp', 'N/A')}\n\n")
            f.write(f"**Models Directory**: {self.report['models_directory']}\n\n")
            
            f.write("## 🔧 Lock Status\n")
            lock_status = self.report.get("lock_status", {})
            f.write(f"- Lock Files Found: {len(lock_status.get('lock_files_found', []))}\n")
            f.write(f"- Lock Files Deleted: {len(lock_status.get('lock_files_deleted', []))}\n")
            f.write(f"- Processes Holding Locks: {len(lock_status.get('processes_holding_locks', []))}\n\n")
            
            f.write("## 🗑️ Deleted Models\n")
            for model in self.report.get("deleted_models", []):
                f.write(f"- {model}\n")
            f.write("\n")
            
            f.write("## ⚡ Downloaded Models\n")
            for model in self.report.get("downloaded_models", []):
                f.write(f"- {model['repo']} / {model['file']}\n")
            f.write("\n")
            
            f.write("## 🧪 Test Results\n")
            test_results = self.report.get("test_results", {})
            for test_name, test_data in test_results.get("tests", {}).items():
                f.write(f"- {test_name.capitalize()} Test: {test_data.get('status', 'N/A')}\n")
            f.write("\n")
            
            f.write("## 🔄 Configuration Updates\n")
            config_updates = self.report.get("config_updates", {})
            f.write(f"- Files Updated: {len(config_updates.get('files_updated', []))}\n")
            f.write(f"- Files Not Found: {len(config_updates.get('files_not_found', []))}\n")
            f.write(f"- Errors: {len(config_updates.get('errors', []))}\n\n")
        
        summary = {
            "json_report": str(json_report_path),
            "markdown_report": str(md_report_path)
        }
        
        self.report["migration_summary"] = summary
        print(f"✅ JSON report saved to: {json_report_path}")
        print(f"✅ Markdown report saved to: {md_report_path}")
        
        return summary
    
    def execute_full_migration(self, lock_fix_mode: bool = False, 
                             delete_models: bool = False,
                             model_repo: str = None,
                             model_file: str = None,
                             target_dir: str = None):
        """Execute the full migration process"""
        import time
        self.report["execution_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.lock_fix_mode = lock_fix_mode
        
        print("🤖 ZombieCoder Local Model Agent")
        print("=" * 40)
        
        # Step 1: Fix lock files if requested
        if lock_fix_mode:
            self.fix_lock_files()
        
        # Step 2: Identify safe to delete models
        safe_delete_list = self.identify_safe_delete_models()
        
        # Step 3: Delete models if requested
        if delete_models and safe_delete_list:
            self.delete_models(safe_delete_list)
        
        # Step 4: Download new model if specified
        if model_repo and model_file and target_dir:
            download_result = self.download_model(model_repo, model_file, target_dir)
            
            # Step 5: Run tests if download was successful
            if download_result["status"] == "completed":
                # Get the actual model name from target directory
                model_name = target_dir
                test_results = self.run_model_tests(model_name)
                
                # Step 6: Update configurations
                model_path = str(self.models_dir / target_dir / model_file)
                self.update_configurations(model_path)
        
        # Step 7: Generate migration summary
        self.generate_migration_summary()
        
        print("\n✅ Migration process completed!")
        return self.report

def main():
    """Main entry point"""
    agent = ZombieCoderLocalAgent()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="ZombieCoder Local Model Agent")
    parser.add_argument("--lock-fix", action="store_true", help="Fix lock files")
    parser.add_argument("--delete-models", action="store_true", help="Delete safe models")
    parser.add_argument("--model-repo", help="Model repository to download from")
    parser.add_argument("--model-file", help="Specific model file to download")
    parser.add_argument("--target-dir", help="Target directory for download")
    
    args = parser.parse_args()
    
    # Execute migration with provided arguments
    agent.execute_full_migration(
        lock_fix_mode=args.lock_fix,
        delete_models=args.delete_models,
        model_repo=args.model_repo,
        model_file=args.model_file,
        target_dir=args.target_dir
    )

if __name__ == "__main__":
    main()
