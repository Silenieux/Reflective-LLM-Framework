
from llama_cpp import Llama

# Load model once using CPU
llm = Llama(
    model_path = "models/MythoMax-L2-13b.Q4_K_M.gguf",
    n_ctx=2048,
    n_threads=12,
    use_mlock=True,
    verbose=False
)

def generate_reflective_response(context_block, user_input):
    prompt = (
        f"{context_block}\n\n"
        f"Customer: {user_input}\n"
        f"Assistant:"
    )
    output = llm(prompt, max_tokens=256, stop=["Customer:", "Assistant:"])
    return output["choices"][0]["text"].strip()



