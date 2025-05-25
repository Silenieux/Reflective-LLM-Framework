from sqlite_store import insert_memory, init_db
from sentence_transformers import SentenceTransformer
import numpy as np

init_db()

model = SentenceTransformer("all-MiniLM-L6-v2")

seed_entries = [
    {
        "Title": "Angry to Calm — Refund offered",
        "Summary": "Customer upset over late delivery, calmed after apology and escalation offer.",
        "Reflective Prompt": "How should an assistant respond when a customer becomes calm after an empathetic apology?",
        "Bias Tags": ["tone-shift", "de-escalation", "retention"],
        "Memory Type": "Empathy Case",
        "Continuity Cue": "Post-Anger Stability",
        "Reflection Status": "Reinforce",
        "tone_context": {"before": "tense", "after": "calm"}
    },
    {
        "Title": "Sarcasm Management",
        "Summary": "Customer used sarcasm. Agent kept tone neutral, clarified issue.",
        "Reflective Prompt": "How should sarcasm be handled without escalating tension?",
        "Bias Tags": ["tone-modulation", "neutrality"],
        "Memory Type": "Tone Handling",
        "Continuity Cue": "Sarcasm Neutralization",
        "Reflection Status": "Reinforce",
        "tone_context": {"before": "mocking", "after": "neutral"}
    }
]

for entry in seed_entries:
    text_to_embed = entry["Summary"] + " " + entry["Reflective Prompt"]
    emb = model.encode([text_to_embed])[0]
    insert_memory(entry, np.array(emb))

print("✅ Seed entries added to symbolic_memory.db.")