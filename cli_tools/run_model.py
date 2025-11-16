import argparse
import json
import requests
import os
import sys

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# মডেল কনফিগ লোড
config_path = os.path.join(script_dir, "models_config.json")
with open(config_path, encoding='utf-8') as f:
    models = json.load(f)

# সার্ভার থেকে মডেল লিস্ট পাওয়া
try:
    response = requests.get("http://127.0.0.1:8007/api/tags", timeout=5)
    if response.status_code == 200:
        server_models = [m['name'] for m in response.json()['models']]
    else:
        server_models = [m['name'] for m in models]  # Fallback to config models
except:
    server_models = [m['name'] for m in models]  # Fallback to config models

parser = argparse.ArgumentParser(description="Run models from ZombieCoder server")
parser.add_argument("--model", required=True, help="Model name to run")
parser.add_argument("--input", required=True, help="Input prompt for the model")
args = parser.parse_args()

# মডেল যাচাই
if args.model not in server_models:
    print(f"Error: Model '{args.model}' not found. Available models: {', '.join(server_models)}")
    exit(1)

# সার্ভার কল
url = f"http://127.0.0.1:8007/api/generate"
response = requests.post(url, json={"model": args.model, "prompt": args.input})

# আউটপুট দেখানো
print("=== Model Output ===")
try:
    # Handle encoding issues
    output = json.dumps(response.json(), ensure_ascii=False, indent=2)
    print(output.encode('utf-8').decode('utf-8'))
except:
    # Fallback for encoding issues
    try:
        print(response.text.encode('utf-8').decode('utf-8'))
    except:
        print("Error: Could not display output due to encoding issues")