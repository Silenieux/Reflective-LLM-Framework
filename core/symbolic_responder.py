# symbolic_responder.py
# Generates tone-aware replies using symbolic memory examples

import json
import random
import textwrap
from datetime import datetime


# Loads all symbolic memory entries from JSON
# Validates expected structure and sorts by timestamp

def load_symbolic_memory(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Ensure all entries have required fields
    valid_entries = []
    for entry in data:
        if "tone_context" in entry and "Summary" in entry:
            if "before" in entry["tone_context"] and "after" in entry["tone_context"]:
                valid_entries.append(entry)

    # Optional: sort by timestamp if present
    valid_entries.sort(key=lambda e: e.get("timestamp", datetime.now().isoformat()))
    return valid_entries


def generate_symbolic_reply(query_tone, memory_db):
    candidates = [
        entry for entry in memory_db
        if entry.get("tone_context", {}).get("before") == query_tone
    ]

    if not candidates:
        return f"[No symbolic match for tone '{query_tone}']"

    choice = random.choice(candidates)
    summary = choice.get("Summary", "No summary found.")
    symbolic_tag = f"[TONE SHIFT: {query_tone} → {choice['tone_context'].get('after', 'unknown')}]"
    hashtags = " ".join(f"#{tag}" for tag in choice.get("Bias Tags", []))

    return format_response(symbolic_tag, summary, hashtags)


def format_response(tag, summary, tags, width=48):
    return "\n".join([
        tag,
        textwrap.fill(summary, width=width),
        tags
    ])


# Example usage
if __name__ == "__main__":
    db = load_symbolic_memory("symbolic_memory_seed.json")
    print(generate_symbolic_reply("sarcastic", db))
