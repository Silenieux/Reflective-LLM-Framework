import json
from pathlib import Path

MEMORY_PATH = Path("memory/symbolic_memory_seed.json")
from symbolic_faiss_core.symbolic_searcher import search_memory
from symbolic_faiss_core.symbolic_searcher import search_memory

def get_memory_context(query, top_k=1):
    results = search_memory(query, k=top_k)
    if results:
        match = results[0]
        return match, match.get("tone_context", {"before": "neutral", "after": "neutral"})
    return {}, {"before": "neutral", "after": "neutral"}
