import streamlit as st
import sqlite3
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import time
from datetime import datetime
import pandas as pd
import os
from pathlib import Path
import requests

# Streamlit config must be first
st.set_page_config(page_title="Reflective Assistant", layout="wide")

# Initialize
conn = sqlite3.connect("memory/reflective_memory.db")
cursor = conn.cursor()

# Ensure the reflective_memory table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS reflective_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    summary TEXT NOT NULL,
    reflective_prompt TEXT NOT NULL,
    tone_before TEXT,
    tone_after TEXT
)
""")
conn.commit()

# Ensure FAISS index exists
INDEX_PATH = "memory/reflective_memory.index"
if not os.path.exists(INDEX_PATH):
    dim = 384  # MiniLM-L6-v2 embedding dimension
    faiss_index = faiss.IndexIDMap(faiss.IndexFlatL2(dim))
    faiss.write_index(faiss_index, INDEX_PATH)

# Load embedding model
_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


from llm.llm_router import swap_llm
from core.faiss_core.vector_search import get_similar_memories
from core.memory_handler import fetch_top_memories  # patched

def clean_input(text):
    return text.replace("User:", "").replace("Assistant:", "").strip()

def query_llm(prompt, recursive=False):
    try:
        model_key = suggest_model_swap(prompt) or "mythomax"
        endpoint = swap_llm(model_key)
        system_prompt = "You are a compassionate reflective assistant. Respond thoughtfully."
        name = st.session_state.get("name_override", "AI Assistant")
        full_prompt = f"{system_prompt}\nUser: {prompt}\n{name}:"
        response = requests.post(endpoint, json={"prompt": full_prompt, "max_tokens": 512, "stop": ["</s>"]})

        if response.status_code != 200:
            return f"[LLM ERROR] HTTP {response.status_code}: {response.text}"

        result = response.json()
        initial_response = result.get('text', '').strip()

        if recursive:
            time.sleep(0.5)
            reflection_prompt = f"You just responded: \"{initial_response}\"\nNow reflect: Was that response accurate, kind, useful, or contextually aware? If not, how would you revise it?"
            reflection_resp = requests.post(endpoint, json={"prompt": reflection_prompt, "max_tokens": 256, "stop": ["</s>"]})
            if reflection_resp.status_code == 200:
                reflection_response = reflection_resp.json().get('text', '').strip()
                return f"{initial_response}\n\n[Reflection]\n{reflection_response}"
        return initial_response

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"[LLM ERROR] {str(e)}"

# Reinstate full original functionality below this point

def save_memory(summary, prompt, tone_b, tone_a):
    cursor.execute("INSERT INTO reflective_memory (summary, reflective_prompt, tone_before, tone_after) VALUES (?, ?, ?, ?)",
                   (summary, prompt, tone_b, tone_a))
    conn.commit()
    embedding = get_embedder().encode([summary], convert_to_numpy=True)[0].astype("float32")
    index = faiss.read_index(INDEX_PATH)
    new_id = cursor.lastrowid
    index.add_with_ids(np.array([embedding]), np.array([new_id]))
    faiss.write_index(index, INDEX_PATH)

# patched: unified tone-aware memory search
def search_memory(cue, tone_filter=None, top_k=3):
    return fetch_top_memories(
        cursor=cursor,
        embedder=get_embedder(),
        cue=cue,
        index_path=INDEX_PATH,
        top_k=top_k,
        tone_filter=tone_filter
    )

