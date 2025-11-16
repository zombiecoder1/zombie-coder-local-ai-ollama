import requests
import json

# Test the model with a simple English prompt first
url = "http://localhost:8007/api/chat"
payload = {
    "model": "phi-2-gguf",
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "max_tokens": 50
}

print("Sending request to model...")
response = requests.post(url, json=payload)

print(f"Status code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print("Response received:")
    print(json.dumps(data, indent=2))
else:
    print(f"Error: {response.text}")