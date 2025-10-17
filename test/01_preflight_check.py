import sys, json, os, requests

def main():
    base = 'http://127.0.0.1:8155'
    out = {"ok": True, "checks": {}}
    try:
        r = requests.get(f"{base}/health", timeout=5).json()
        out["checks"]["health"] = r
        if r.get("status") != "healthy":
            out["ok"] = False
    except Exception as e:
        out["ok"] = False
        out["checks"]["health_error"] = str(e)

    try:
        r = requests.get(f"{base}/runtime/config", timeout=5).json()
        out["checks"]["runtime_config"] = r
        if not r.get("exists"):
            out["ok"] = False
    except Exception as e:
        out["ok"] = False
        out["checks"]["runtime_config_error"] = str(e)

    try:
        r = requests.get(f"{base}/models/installed", timeout=5).json()
        out["checks"]["installed"] = r
        models = r.get("models", [])
        # Check for GGUF models (tinyllama-gguf preferred)
        has_gguf = any(m.get("name") == "tinyllama-gguf" for m in models)
        has_any = any(m.get("name") in ("tinyllama-gguf", "tinyllama", "qwen0_5b") for m in models)
        if not has_any:
            out["ok"] = False
        out["checks"]["has_gguf_model"] = has_gguf
    except Exception as e:
        out["ok"] = False
        out["checks"]["installed_error"] = str(e)

    print(json.dumps(out, indent=2))
    sys.exit(0 if out["ok"] else 1)

if __name__ == '__main__':
    main()


