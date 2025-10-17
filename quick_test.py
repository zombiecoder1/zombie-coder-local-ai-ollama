import requests

models = ['phi-2', 'tinyllama', 'tinyllama-gguf']
base = 'http://localhost:8155'

print("Model Format Validation:\n")
for m in models:
    r = requests.get(f'{base}/registry/validate/{m}')
    v = r.json()
    status = "✅" if v.get('valid') else "❌"
    print(f"{status} {m}: {v['format']} - {v.get('message', '')[:50]}")

print("\n\nInstalled Models:")
r = requests.get(f'{base}/registry/models')
data = r.json()
for m in data.get('installed', []):
    print(f"  - {m['name']} ({m['size_mb']/1024:.1f} GB)")

