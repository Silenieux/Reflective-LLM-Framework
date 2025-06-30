import numpy as np
import faiss

def save_memory(cursor, conn, embedder, summary, prompt, tone_b, tone_a, index_path):
    cursor.execute(
        "INSERT INTO reflective_memory (summary, reflective_prompt, tone_before, tone_after) VALUES (?, ?, ?, ?)",
        (summary, prompt, tone_b, tone_a)
    )
    conn.commit()
    embedding = embedder.encode([summary]).astype("float32")
    index = faiss.read_index(index_path)
    new_id = cursor.lastrowid
    index.add_with_ids(embedding, np.array([new_id]))
    faiss.write_index(index, index_path)

def get_memory_match(cursor, embedder, cue, index_path, threshold=0.78, top_k=3, tone_filter=None):
    embedding = embedder.encode([cue]).astype("float32")
    index = faiss.read_index(index_path)
    D, I = index.search(embedding, top_k)
    matches = []
    for i in range(top_k):
        sim = 1 - D[0][i]
        if sim >= threshold:
            entry_id = int(I[0][i])
            cursor.execute(
                "SELECT summary, reflective_prompt, tone_before, tone_after FROM reflective_memory WHERE id = ?",
                (entry_id,)
            )
            result = cursor.fetchone()
            if result:
                if tone_filter is None or result[2] == tone_filter or result[3] == tone_filter:
                    matches.append({
                        "id": entry_id,
                        "summary": result[0],
                        "prompt": result[1],
                        "similarity": round(sim, 3),
                        "tone_before": result[2],
                        "tone_after": result[3]
                    })
    return matches if matches else []

def fetch_top_memories(cursor, embedder, cue, index_path, top_k=3, tone_filter=None):
    return get_memory_match(cursor, embedder, cue, index_path, top_k=top_k, tone_filter=tone_filter)
