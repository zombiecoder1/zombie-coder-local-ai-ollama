import sys, json, requests

BASE = 'http://127.0.0.1:8155'

def main():
    out = {"ok": True, "checks": {}}
    try:
        tags = requests.get(f"{BASE}/api/tags", timeout=10).json()
        out["checks"]["tags_shape_ok"] = isinstance(tags, dict) and isinstance(tags.get('models', []), list)
        if not out["checks"]["tags_shape_ok"]:
            out["ok"] = False
    except Exception as e:
        out["checks"]["tags_error"] = str(e); out["ok"] = False

    # generate should be 200 when runtime is ready, else 409; both acceptable forms
    try:
        r = requests.post(f"{BASE}/api/generate", json={"model":"tinyllama","prompt":"ping"}, timeout=10)
        out["checks"]["generate_code"] = r.status_code
        if r.status_code not in (200, 409):
            out["ok"] = False
    except Exception as e:
        out["checks"]["generate_error"] = str(e); out["ok"] = False

    print(json.dumps(out, indent=2))
    sys.exit(0 if out["ok"] else 1)

if __name__ == '__main__':
    main()


