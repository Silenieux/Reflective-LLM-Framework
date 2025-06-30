import faiss
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

def reflective_fallback_reply(user_query, tone_context=None, tone_meta=None, top_k=3, show_debug=True):
    import inspect
    print("USING FUNCTION DEFINED IN:", inspect.getfile(reflective_fallback_reply))
    print("reflective_fallback_reply() running — tone_context:", tone_context)
    if tone_meta:
        print("reflective_fallback_reply() tone_meta:", tone_meta)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    memory_path = Path(__file__).resolve().parent.parent / "memory" / "reflective_memory_seed.json"

    import sqlite3

    db_path = Path(__file__).resolve().parent.parent / "memory" / "reflective_memory.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Rebuild table and seed data
    cursor.execute("DROP TABLE IF EXISTS reflective_memory")
    cursor.execute("""
    CREATE TABLE reflective_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        summary TEXT NOT NULL,
        reflective_prompt TEXT,
        tone_before TEXT,
        tone_after TEXT
    )
    """)

    seed_entries = [
        # Retail
        ("Customer was upset about return policy.", "How can empathy reduce tension over strict policies?", "frustrated", "calm"),
        ("Customer thanked the associate after receiving help.", "What leads to gratitude in routine interactions?", "neutral", "grateful"),
        # Hardware
        ("User confused by drywall anchor weight limits.", "How can hardware safety be better explained?", "confused", "hopeful"),
        ("Sawdust created during cutting created breathing issues.", "Should tool use always include safety tips?", "neutral", "tense"),
        # IT
        ("User clicked a phishing link unknowingly.", "How can tone impact IT escalation paths?", "resigned", "neutral"),
        ("Admin locked out due to expired 2FA.", "What options can de-escalate locked credential frustrations?", "frustrated", "curious"),
        # Social Media
        ("Post mocking a product got viral support.", "How does sarcasm get misinterpreted as insight?", "sarcastic", "amused"),
        ("Content creator accused of copying style.", "What tone builds bridges in defensive replies?", "hostile", "neutral"),
        # Assistant UX
        ("AI failed to clarify calendar invite time zone.", "When is over-clarification better than confusion?", "confused", "neutral"),
        ("User thanked assistant for detecting tone error.", "How can assistants course-correct with tact?", "grateful", "grateful")
    ]

    cursor.executemany("""
        INSERT INTO reflective_memory (summary, reflective_prompt, tone_before, tone_after)
        VALUES (?, ?, ?, ?)
    """, seed_entries)
    conn.commit()

    rows = cursor.execute("SELECT summary, reflective_prompt, tone_before, tone_after FROM reflective_memory").fetchall()
    all_entries = []
    for summary, prompt, before, after in rows:
        all_entries.append({
            "Summary": summary,
            "Reflective Prompt": prompt,
            "tone_context": {"before": before, "after": after}
        })

    conn.close()

    if tone_context:
        tone_filter = tone_context.get("after") or tone_context.get("before") or "neutral"
        filtered = [entry for entry in all_entries if entry.get("tone_context", {}).get("after") == tone_filter]
        if not filtered:
            print(f"[warn] No entries match tone '{tone_filter}'. Using all memory.")
            filtered = all_entries
    else:
        tone_filter = "neutral"
        filtered = all_entries

    texts = [entry["Summary"] + " " + entry.get("Reflective Prompt", "") for entry in filtered]
    vectors = model.encode(texts, convert_to_numpy=True)

    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    q_vec = model.encode([user_query], convert_to_numpy=True)
    D, I = index.search(q_vec, top_k)

    results = [filtered[i] for i in I[0] if i < len(filtered)]

    if not results or D[0][0] > 1.5:
        print("[fallback] No strong vector match — reverting to full memory")
        texts = [entry["Summary"] + " " + entry.get("Reflective Prompt", "") for entry in all_entries]
        vectors = model.encode(texts, convert_to_numpy=True)
        index = faiss.IndexFlatL2(vectors.shape[1])
        index.add(vectors)
        D, I = index.search(q_vec, top_k)
        results = [all_entries[i] for i in I[0] if i < len(all_entries)]

    if show_debug:
        print(f"\nTop-{top_k} FAISS matches (tone='{tone_filter}'):")
        for dist, idx in zip(D[0], I[0]):
            if idx < len(filtered):
                print(f"  ({dist:.3f}) {filtered[idx]['Summary'][:80]}...")

    if not results:
        return "[No matching reflective memory found.]"

    top = results[0]
    print("[DEBUG] Returning response:\n", top['Summary'], "\n", top.get('Reflective Prompt', ''))

    response = top['Summary'] + "\n" + top.get('Reflective Prompt', '')

    if tone_meta:
        emotion = tone_meta.get("emotion")
        if emotion == "burnout":
            response += "\nNote: This may indicate fatigue in handling repeated concerns."
        elif emotion == "absurd":
            response = "\ud83c\udf00 Reality spirals oddly today...\n" + response
        elif emotion == "hostile":
            response = "\u26a0\ufe0f Redirecting with caution:\n" + response

    return response
