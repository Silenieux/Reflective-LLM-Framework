import sqlite3
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Setup
model = SentenceTransformer("all-MiniLM-L6-v2")
conn = sqlite3.connect("reflective_memory.db")
cursor = conn.cursor()

# FAISS index (must match dimensions of embedding)
# Assume it's initialized and persistent
# faiss_index = faiss.IndexFlatL2(384)

def save_to_reflective_memory(cue, reflection, tone_before, tone_after):
    # 1. Embed the cue
    embedding = model.encode(cue).astype("float32")

    # 2. Save to SQLite
    cursor.execute("""
        INSERT INTO reflective_memory (cue, reflection, tone_before, tone_after)
        VALUES (?, ?, ?, ?)
    """, (cue, reflection, tone_before, tone_after))
    conn.commit()

    # 3. Get row ID and save to FAISS
    entry_id = cursor.lastrowid
    faiss_index.add_with_ids(embedding.reshape(1, -1), np.array([entry_id]))

    return entry_id
