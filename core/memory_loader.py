
import os
import json

def load_memory(log_path):
    if not os.path.exists(log_path):
        print("[error] memory_log.json not found.")
        return []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("[error] Failed to parse memory log.")
        return []
