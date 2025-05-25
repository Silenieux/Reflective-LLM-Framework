import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sentence_transformers import SentenceTransformer
from sqlite_store import fetch_all_entries, insert_memory
from vector_search import search_memory  # Keep this if FAISS is still used
from modules.atomic.format_context import format_context
import numpy as np
from core.llama_wrapper import generate_response


LOG_PATH = os.getenv("LOG_PATH", "./logs/memory_log.json")
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "./logs/rag_context.txt")
MODEL_NAME = "all-MiniLM-L6-v2"
LLAMA_MODEL_PATH = os.getenv("LLM_MODEL_PATH", "./models/MythoMax-L2-13B.Q4_K_M.gguf")
TOP_K = 5

def main():
    print("[*] Launch UI? (y/n): ", end="")
    choice = input().strip().lower()
    if choice == "y":
        launcher_path = os.path.join(os.path.dirname(__file__), "launcher.py")
        if os.path.exists(launcher_path):
            print("[ui] Launching assistant UI...")
            os.system(f'python "{launcher_path}"')
            return
        else:
            print("[error] UI launcher not found. Proceeding with CLI...")

    print("[*] Verifying memory log file...")
    if not os.path.exists(LOG_PATH):
        print(f"[error] Memory log file not found at: {LOG_PATH}")
        return

    print("[*] Loading symbolic memory from SQLite...")
    model = SentenceTransformer(MODEL_NAME)
    
    entry_pairs = fetch_all_entries()
    if not entry_pairs:
        print("[error] No entries found in database.")
        return
    

    entries, embeddings = zip(*entry_pairs)
    
    
def cosine_search(embeddings, entries, query, model, top_k):
    from numpy import dot
    from numpy.linalg import norm

    query_emb = model.encode([query])[0]

    def cosine_sim(a, b):
        return dot(a, b) / (norm(a) * norm(b))

    scores = [(cosine_sim(query_emb, emb), e) for e, emb in zip(entries, embeddings)]
    scores.sort(reverse=True, key=lambda x: x[0])
    return [e for _, e in scores[:top_k]]


        query_emb = model.encode([query])[0]

        def cosine_sim(a, b):
        return dot(a, b) / (norm(a) * norm(b))

        scores = [(cosine_sim(query_emb, emb), e) for e, emb in zip(entries, embeddings)]
        scores.sort(reverse=True, key=lambda x: x[0])
        return [e for _, e in scores[:top_k]]
 

        query = input("\n[?] Enter a symbolic query for reflection:\n> ").strip()
        print(f"\n[*] Searching memory for: \"{query}\"")
        top_entries = cosine_search(embeddings, entries, query, model, TOP_K)

        if not top_entries:
            print("[error] No relevant memory entries found.")
            return

        top_block = format_context(top_entries[0])
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(top_block)

        print("\n[okay] Top result written to rag_context.txt.")

        user_msg = input("\n[+] Enter customer message:\n> ").strip()
        print("\n[~] Generating response...\n")
        response = generate_response(top_block, user_msg, LLAMA_MODEL_PATH)

        print("[Response]:\n")
        print(response)

new_entry = {
        "Title": query[:60],
        "Summary": response[:120],
        "Reflective Prompt": query,
        "Bias Tags": ["auto-logged"],
        "Memory Type": "Auto-Reflection",
        "Continuity Cue": "RAG-assisted",
        "Reflection Status": "Reinforce",
        "tone_context": {"before": "?", "after": "?"}
}
embedding = model.encode([response])[0]
insert_memory(new_entry, np.array(embedding))
print("\n[log] Response inserted into symbolic_memory.db.")

if __name__ == "__main__":
    main()
