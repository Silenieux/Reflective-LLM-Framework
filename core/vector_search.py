
import faiss
import numpy as np

def create_embeddings(texts, model):
    return model.encode(texts, convert_to_numpy=True)

def build_index(model, entries):
    summaries = [
        e.get("Summary", "") + " " + e.get("Reflective Prompt", "")
        for e in entries
    ]
    embeddings = create_embeddings(summaries, model)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index, summaries

def search_memory(index, entries, query, model, top_k):
    query_embedding = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, top_k)
    return [entries[i] for i in indices[0]]
