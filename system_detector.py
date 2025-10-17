#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import platform
from typing import Dict, Optional

import psutil


def detect_system_info() -> Dict:
    """Detect basic system information and assign a performance tier."""
    ram_gb = psutil.virtual_memory().total / (1024 ** 3)

    if ram_gb < 6:
        tier = "entry_level"
    elif ram_gb < 12:
        tier = "mid_range"
    elif ram_gb < 24:
        tier = "good"
    elif ram_gb < 48:
        tier = "high_end"
    else:
        tier = "enthusiast"

    gpu_info: Optional[str] = "Not detected"
    try:
        import subprocess
        if platform.system() == "Windows":
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
                if len(lines) > 1:
                    gpu_info = lines[1]
    except Exception:
        pass

    return {
        "total_ram_gb": round(ram_gb, 2),
        "cpu_model": platform.processor() or "Unknown",
        "gpu_info": gpu_info,
        "tier": tier,
        "os": f"{platform.system()} {platform.release()}",
    }


