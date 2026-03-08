import os
import json
import platform
import subprocess
from pathlib import Path

BASE_DIR = Path("e:/SohanCore/sohan_ai_agent")

def _list_dir_safe(path: Path, limit: int = 40):
    try:
        entries = []
        for i, p in enumerate(sorted(path.iterdir())):
            if i >= limit:
                entries.append("...truncated...")
                break
            entries.append(p.name + ("/" if p.is_dir() else ""))
        return entries
    except Exception:
        return []

def _running_processes(limit: int = 15):
    try:
        out = subprocess.check_output(["tasklist"], creationflags=0x08000000).decode(errors="ignore")
        lines = out.splitlines()[3:3+limit]
        return lines
    except Exception:
        return []

def get_environment_snapshot():
    cwd = Path.cwd()
    return {
        "os": platform.platform(),
        "cwd": str(cwd),
        "cwd_listing": _list_dir_safe(cwd),
        "project_root": str(BASE_DIR),
        "project_listing": _list_dir_safe(BASE_DIR),
        "running_processes": _running_processes(),
    }
