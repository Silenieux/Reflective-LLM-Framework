import os
import json
import sys
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from llama_cpp import Llama

# === CONFIGURATION ===
LOG_PATH = "D:/LLM_Memory/memory_log.json"
OUTPUT_PATH = "D:/LLM_Memory/rag_context.txt"
MODEL_NAME = "all-MiniLM-L6-v2"
LLAMA_MODEL_PATH = "C:/Users/Scrambles/llama.cpp/models/MythoMax-L2-13B.Q4_K_M.gguf"
TOP_K = 5

# === Load memory entries ===
def load_memory():
    if not os.path.exists(LOG_PATH):
        print("[error] memory_log.json not found.")
        return []
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("[error] Failed to parse memory log.")
        return []

# === Embed text with SentenceTransformer ===
def create_embeddings(texts, model):
    return model.encode(texts, convert_to_numpy=True)

# === Build FAISS index ===
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

# === Search and retrieve top K matches ===
def search_memory(index, entries, query, model, top_k=TOP_K):
    query_embedding = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, top_k)
    return [entries[i] for i in indices[0]]

# === Format result as a prompt block ===
def format_context(entry, label="ToneRecall"):
    summary = entry.get("Summary", "").strip()
    prompt = entry.get("Reflective Prompt", "").strip()
    return f"[KNOWLEDGE={label}]\n{summary} {prompt}".strip()

# === Generate reply using LLaMA model ===
def generate_response(context_block, user_msg):
    model = Llama(
        model_path=LLAMA_MODEL_PATH,
        n_ctx=4096,
        n_threads=8,
        n_batch=512,
        verbose=False
    )

    full_prompt = (
        f"You are an AI support assistant. Use the following knowledge to guide your reply.\n\n"
        f"{context_block}\n\n"
        f"[CUSTOMER MESSAGE]\n{user_msg}\n\n"
        f"[ASSISTANT REPLY]"
    )

    response = model.create_chat_completion(
        messages=[
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.7,
        max_tokens=256,
    )

    return response['choices'][0]['message']['content']

# === Main logic ===
def main():
    print("[*] Loading symbolic memory...")
    memory = load_memory()
    if not memory:
        print("[error] No entries found.")
        return

    model = SentenceTransformer(MODEL_NAME)
    index, _ = build_index(model, memory)

    query = input("\n[?] Enter a symbolic query for reflection:\n> ").strip()
    print(f"\n[*] Searching memory for: \"{query}\"")
    top_entries = search_memory(index, memory, query, model)

    if not top_entries:
        print("[error] No relevant memory entries found.")
        return

    top_block = format_context(top_entries[0])
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(top_block)

    print("\n[okay] Top result written to rag_context.txt.")

    user_msg = input("\n[+] Enter customer message:\n> ").strip()
    print("\n[~] Generating response...\n")
    reply = generate_response(top_block, user_msg)
    print("[Response]:\n")
    print(reply)

if __name__ == "__main__":
    main()