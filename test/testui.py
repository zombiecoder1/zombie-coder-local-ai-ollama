# -*- coding: utf-8 -*-
import json, sys, requests

BASE = 'http://127.0.0.1:8155'

def get(path, timeout=10):
    r = requests.get(BASE + path, timeout=timeout)
    return r.status_code, (r.json() if 'application/json' in r.headers.get('Content-Type','') else r.text)

out = {"ok": True}

code, installed = get('/models/installed')
out['installed_code'] = code
out['installed_count'] = (installed.get('count') if isinstance(installed, dict) else None)

code, runtime = get('/runtime/status')
out['runtime_code'] = code
models_ok = isinstance(runtime, dict) and isinstance(runtime.get('models'), list)
out['runtime_models_ok'] = models_ok

print(json.dumps(out, indent=2))
sys.exit(0 if (out['installed_code']==200 and out['runtime_code']==200 and models_ok) else 1)
