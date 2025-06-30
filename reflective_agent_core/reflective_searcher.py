import faiss
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

model = SentenceTransformer("all-MiniLM-L6-v2")

base_path = Path(__file__).resolve().parent.parent
memory_db = base_path / "memory" / "reflective_memory.db"
faiss_index_path = base_path / "memory" / "reflective_index.faiss"


def query_reflective_memory(query_text, tone_context=None, top_k=3):
    try:
        conn = sqlite3.connect(memory_db)
        cursor = conn.cursor()
        cursor.execute("SELECT id, summary, reflective_prompt FROM reflective_memory")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return []

        index = faiss.read_index(str(faiss_index_path))
        query_vector = model.encode([query_text])
        distances, indices = index.search(query_vector, top_k)

        results = []
        for idx in indices[0]:
            if idx < len(rows):
                row = rows[idx]
                results.append({
                    "id": row[0],
                    "summary": row[1],
                    "reflective_prompt": row[2]
                })

        return results

    except Exception as e:
        raise RuntimeError(f"Failed to query reflective memory: {e}")
