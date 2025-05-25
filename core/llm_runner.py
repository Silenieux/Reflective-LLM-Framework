from llama_cpp import Llama

# You can eventually load this from a config file
MODEL_PATH = os.getenv("LLM_MODEL_PATH", "./models/MythoMax-L2-13B.Q4_K_M.gguf")

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,
    n_threads=12
)

def generate_response(context: str, user_msg: str, max_tokens=512) -> str:
    prompt = (
        "[TONE=adaptive] [MEMORY=reflection]\n"
        f"{context}\n\n"
        f"Customer: {user_msg}\n"
        f"Assistant:"
    )
    
    result = llm(
        prompt,
        max_tokens=max_tokens,
        stop=["Customer:", "Assistant:", "</s>"]
    )
    
    return result["choices"][0]["text"].strip()
