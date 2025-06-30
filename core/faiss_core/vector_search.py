import sqlite3
import numpy as np
import faiss
import os
from sentence_transformers import SentenceTransformer

INDEX_PATH = "memory/reflective_memory.index"
DB_PATH = "memory/reflective_memory.db"

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

def get_similar_memories(query, top_k=5, current_tone=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, summary, tone_before, tone_after FROM reflective_memory")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    summaries = [row[1] for row in rows]
    tones_before = {row[0]: row[2] for row in rows}
    tones_after = {row[0]: row[3] for row in rows}
    ids = [row[0] for row in rows]

    embedder = get_embedder()
    query_vec = embedder.encode([query])[0].astype("float32")

    index = faiss.read_index(INDEX_PATH)
    if index.ntotal == 0:
        return []

    D, I = index.search(np.array([query_vec]), top_k)

    id_to_summary = dict(zip(ids, summaries))
    results = []
    for idx in I[0]:
        if idx in id_to_summary:
            # If tone is passed in, filter out mismatches
            if current_tone:
                if tones_before.get(idx) != current_tone and tones_after.get(idx) != current_tone:
                    continue
            results.append(id_to_summary[idx])

    return results

    #EXPERIMENTAL!
def web_search(query):
    import duckduckgo_search
    from duckduckgo_search import ddg

    try:
        results = ddg(query, max_results=3)
        if results:
            return "\n\n".join([f"- {r['title']}: {r['href']}" for r in results])
        else:
            return "No relevant results found."
    except Exception as e:
        return f"Search failed: {str(e)}"