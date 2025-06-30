# greg_postprocessors.py

# Toggleable dev flag
DEV_REFLECTION = False

# ── Isolate O3-style Final Answer ──
def isolate_final_answer(text: str) -> str:
    markers = ["Answer:", "Final answer:", "So the answer is", "Therefore,", "In conclusion,"]
    for marker in markers:
        if marker.lower() in text.lower():
            parts = text.lower().split(marker.lower())
            if len(parts) > 1:
                return marker + parts[-1].strip()
    return text.strip()

# ── Soft Suppression of Internal Monologue ──
def suppress_open_thinking(text: str) -> str:
    if DEV_REFLECTION:
        return text  # Skip suppression if debugging

    monologue_starts = [
        "first, i need to", "let's break this down", "alright, let's tackle",
        "so, the user is asking", "wait, maybe", "then there's", 
        "however, the user", "i suppose", "next, let's", 
        "but", "perhaps"
    ]

    lines = text.strip().split("\n")
    final_lines = [line for line in lines if not any(line.lower().startswith(p) for p in monologue_starts)]

    return "\n".join(final_lines).strip()

# ── Optional: Logging Trimmer for Dev Mode ──
def log_trimmed_output(prompt: str, raw: str, cleaned: str, filepath: str = "logs/trimmed_reflection.log"):
    if not os.path.exists("logs"):
        os.makedirs("logs")
    with open(filepath, "a", encoding="utf-8") as log:
        log.write(f"\n---\nPrompt:\n{prompt}\n\nRAW:\n{raw}\n\nCLEANED:\n{cleaned}\n")
