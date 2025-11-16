#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script for Model Loader Utilities
"""

import sys
import os

# Add parent directory to path so we can import the scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_model_loader_import():
    """Test that we can import the model loader utilities"""
    print("🧪 Testing Model Loader Utilities Import")
    print("======================================")
    
    try:
        # Try to import the module
        import scripts.model_loader_utils
        print("✅ Successfully imported model_loader_utils")
        
        # Try to create an instance
        loader = scripts.model_loader_utils.ModelLoaderUtils()
        print("✅ Successfully created ModelLoaderUtils instance")
        
        # Try to get models index
        models_index = loader.get_models_index()
        print(f"✅ Successfully retrieved models index with {len(models_index.get('models', []))} models")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_model_loader_import()
    sys.exit(0 if success else 1)