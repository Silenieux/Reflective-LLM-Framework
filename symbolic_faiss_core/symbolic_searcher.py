
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from pathlib import Path

MODEL = SentenceTransformer("all-MiniLM-L6-v2")
INDEX_PATH = Path("memory/symbolic_index.faiss")
META_PATH = Path("memory/symbolic_vectors.json")

def search_memory(query, k=1):
    index = faiss.read_index(str(INDEX_PATH))
    with open(META_PATH) as f:
        entries = json.load(f)

    q_vec = MODEL.encode([query], convert_to_numpy=True)
    D, I = index.search(q_vec, k)

    results = [entries[i] for i in I[0]]
    return results
