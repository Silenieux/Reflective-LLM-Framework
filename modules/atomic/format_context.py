
def format_context(entry, label="ToneRecall"):
    summary = entry.get("Summary", "").strip()
    prompt = entry.get("Reflective Prompt", "").strip()
    return f"[KNOWLEDGE={label}]\n{summary} {prompt}".strip()
