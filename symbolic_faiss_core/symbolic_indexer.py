
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from pathlib import Path

MODEL = SentenceTransformer("all-MiniLM-L6-v2")
MEMORY_PATH = Path("memory/symbolic_memory_seed.json")
INDEX_PATH = Path("memory/symbolic_index.faiss")
META_PATH = Path("memory/symbolic_vectors.json")

def build_index():
    with open(MEMORY_PATH) as f:
        data = json.load(f)

    texts = [entry["Summary"] for entry in data]
    embeddings = MODEL.encode(texts, convert_to_numpy=True)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_PATH))
    META_PATH.write_text(json.dumps(data, indent=2))

    print(f"[ok] FAISS index written with {len(embeddings)} vectors")

if __name__ == "__main__":
    build_index()
