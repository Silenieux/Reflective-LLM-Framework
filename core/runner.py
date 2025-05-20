
import os
from sentence_transformers import SentenceTransformer
from core.memory_loader import load_memory
from core.vector_search import build_index, search_memory
from core.llama_wrapper import generate_response
from modules.atomic.format_context import format_context

LOG_PATH = "D:/LLM_Memory/memory_log.json"
OUTPUT_PATH = "D:/LLM_Memory/rag_context.txt"
MODEL_NAME = "all-MiniLM-L6-v2"
LLAMA_MODEL_PATH = "C:/Users/Scrambles/llama.cpp/models/MythoMax-L2-13B.Q4_K_M.gguf"
TOP_K = 5

def main():
    print("[*] Loading symbolic memory...")
    memory = load_memory(LOG_PATH)
    if not memory:
        print("[error] No entries found.")
        return

    model = SentenceTransformer(MODEL_NAME)
    index, _ = build_index(model, memory)

    query = input("\n[?] Enter a symbolic query for reflection:\n> ").strip()
    print(f"\n[*] Searching memory for: \"{query}\"")
    top_entries = search_memory(index, memory, query, model, TOP_K)

    if not top_entries:
        print("[error] No relevant memory entries found.")
        return

    top_block = format_context(top_entries[0])
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(top_block)

    print("\n[okay] Top result written to rag_context.txt.")

    user_msg = input("\n[+] Enter customer message:\n> ").strip()
    print("\n[~] Generating response...\n")
    reply = generate_response(top_block, user_msg, LLAMA_MODEL_PATH)
    print("[Response]:\n")
    print(reply)

if __name__ == "__main__":
    main()
