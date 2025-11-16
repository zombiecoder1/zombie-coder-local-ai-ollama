#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Model Loader Utilities
"""

import sys
import os

# Add the scripts directory to the path
scripts_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts')
sys.path.insert(0, scripts_dir)

# Now we can import the module directly
import model_loader_utils

def test_model_loader():
    """Test the model loader utilities"""
    print("🧪 Testing Model Loader Utilities")
    print("================================")
    
    # Initialize the loader
    loader = model_loader_utils.ModelLoaderUtils()
    
    # Test getting models index
    print("\n1. Testing models index retrieval...")
    models_index = loader.get_models_index()
    print(f"   Found {len(models_index.get('models', []))} models in index")
    
    # Test endpoint status
    print("\n2. Testing provider endpoints...")
    endpoints = loader.get_provider_endpoints_status()
    all_good = True
    for endpoint, status in endpoints.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {endpoint}")
        if not status:
            all_good = False
    
    # Test lazy loading
    print("\n3. Testing lazy load functionality...")
    result = loader.lazy_load_model("phi-2")
    if result:
        print("   ✅ Lazy load test passed")
    else:
        print("   ❌ Lazy load test failed")
    
    # Test ensuring model resident
    print("\n4. Testing model resident mode...")
    loader.ensure_model_resident("phi-2")
    print("   ✅ Model resident mode test completed")
    
    if all_good and result:
        print("\n🎉 All model loader tests passed!")
        return True
    else:
        print("\n❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = test_model_loader()
    sys.exit(0 if success else 1)