import os
import json

def load_memory(log_path):
    if not os.path.exists(log_path):
        return []

    with open(log_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data  # ← Return list of dicts directly