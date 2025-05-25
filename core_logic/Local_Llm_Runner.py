# local_llm_runner.py
# Provides local symbolic reflection using llama-cpp-python and MythoMax

from llama_cpp import Llama

# Load your local MythoMax model
llm = Llama(
    model_path="models/MythoMax-L2-13b.Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=8,  # adjust depending on your CPU
    verbose=False
)

def reflect_locally(user_msg, tone_context):
    prompt = f"""
You are a symbolic assistant. Reflect on the user's message
in a tone-aware and emotionally intelligent way.

Tone Shift: {tone_context.get('before', '?')} → {tone_context.get('after', '?')}

Message: {user_msg}

Respond concisely with symbolic insight, no external references.
"""

    response = llm(prompt, max_tokens=256, stop=["\n"])
    return response["choices"][0]["text"].strip()
