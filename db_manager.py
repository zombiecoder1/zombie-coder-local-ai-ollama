#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def load_registry(path: Path) -> Dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"models": [], "last_updated": None}


def save_registry(path: Path, data: Dict) -> None:
    data = dict(data)
    data["last_updated"] = data.get("last_updated") or datetime.now().isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def scan_models_directory(models_dir: Path) -> List[Dict]:
    models: List[Dict] = []
    if not models_dir.exists():
        models_dir.mkdir(parents=True, exist_ok=True)
        return models

    for item in models_dir.iterdir():
        if not item.is_dir():
            continue
        # Skip common non-model folders/files
        if item.name in {"__pycache__"}:
            continue
        has_config = (item / "config.json").exists()
        has_weights = any(item.glob("*.bin")) or any(item.glob("*.safetensors")) or any(item.glob("*.gguf"))
        if has_config or has_weights:
            size_mb = sum(f.stat().st_size for f in item.rglob('*') if f.is_file()) / (1024 ** 2)
            models.append({
                "name": item.name,
                "path": str(item),
                "size_mb": size_mb,
                "detected_at": datetime.now().isoformat(),
            })
    return models


