import json
import os
from datetime import datetime

LOG_PATH = os.getenv("LOG_PATH", "./logs/memory_log.json")

def append_to_memory(
    symbolic_query,
    assistant_reply,
    customer_message="",
    tags=None,
    memory_type="Auto-Reflection",
    status="Reinforce",
    tone_context=None,
    suggested_repair=""
):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "symbolic_query": symbolic_query.strip(),
        "customer_message": customer_message.strip(),
        "assistant_reply": assistant_reply.strip(),
        "reflection": "",  # You can optionally prefill this
        "tone_context": tone_context or {},
        "suggested_repair": suggested_repair.strip(),
        "Bias Tags": tags or ["auto-logged"],
        "Memory Type": memory_type,
        "Continuity Cue": "Auto-Logged Session",
        "Reflection Status": status
    }

    try:
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                memory = json.load(f)
        else:
            memory = []
    except json.JSONDecodeError:
        print("[warn] JSON decode error, starting fresh.")
        memory = []

    memory.append(entry)

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

    print("[log] Reflection appended to memory_log.json")
