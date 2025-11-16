import sys, json, time, requests

BASE = 'http://127.0.0.1:8155'

def req(method, path, **kw):
    # Increase default timeout to handle first-token latency
    if 'timeout' not in kw:
        kw['timeout'] = 180
    r = requests.request(method, BASE + path, **kw)
    return r.status_code, (r.json() if 'application/json' in r.headers.get('Content-Type', '') else r.text)

def main():
    out = {"ok": True, "steps": []}

    # Load preferred downloaded model if present (GGUF format)
    preferred = 'tinyllama-gguf'
    # Try tinyllama-gguf first (GGUF format)
    code, data = req('POST', f'/runtime/load/{preferred}?threads=4')
    if code != 200 or (isinstance(data, dict) and data.get('status') not in ('ready','loading')):
        # fallback qwen0_5b
        preferred = 'qwen0_5b'
        code, data = req('POST', f'/runtime/load/{preferred}?threads=4')
        if code != 200 or (isinstance(data, dict) and data.get('status') not in ('ready','loading')):
            # fallback tinyllama (safetensors - may not work)
            preferred = 'tinyllama'
            code, data = req('POST', '/runtime/load/tinyllama?threads=4')
    out["steps"].append({"load": {"code": code, "data": data}})
    if code != 200 or (isinstance(data, dict) and data.get('status') not in ('ready','loading')):
        out["ok"] = False
        print(json.dumps(out, indent=2))
        sys.exit(1)

    # Poll readiness for up to 40s
    deadline = time.time() + 40
    rt = None
    while time.time() < deadline:
        code, rt = req('GET', '/runtime/status', timeout=5)
        if isinstance(rt, dict):
            break
        time.sleep(1)
    out["steps"].append({"runtime": rt})
    ready = False
    port = None
    # Use the loaded model name from response
    target_model = preferred
    if isinstance(data, dict) and 'model' in data:
        target_model = data.get('model')
    if isinstance(rt, dict):
        for m in rt.get('models', []):
            if m.get('model') == target_model and m.get('status') == 'ready':
                ready = True
                port = m.get('port')
                break
    if not ready:
        out["ok"] = False
        print(json.dumps(out, indent=2))
        sys.exit(1)

    # Generate
    payload = {"model":target_model,"prompt":"Hello from test"}
    code, gen = req('POST', '/api/generate', json=payload)
    out["steps"].append({"generate": {"code": code, "data": gen}})
    if code != 200:
        out["ok"] = False
        print(json.dumps(out, indent=2))
        sys.exit(1)

    # Unload
    code, un = req('POST', f'/runtime/unload/{target_model}')
    out["steps"].append({"unload": {"code": code, "data": un}})
    if code != 200:
        out["ok"] = False
        print(json.dumps(out, indent=2))
        sys.exit(1)

    print(json.dumps(out, indent=2))
    sys.exit(0)

if __name__ == '__main__':
    main()


