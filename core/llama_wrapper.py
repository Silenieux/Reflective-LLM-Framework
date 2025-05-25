import requests

def generate_response(context, user_msg, model_path=None):
    full_prompt = (
    "You are a tone-aware customer support assistant.\n"
    "Always begin by assessing the emotional tone and seriousness of the customer’s message.\n"
    "If the situation is absurd *but harmless*, feel free to play along *lightly* while still helping.\n"
    "If the situation involves intimidation, harassment, or real fear, respond calmly, seriously, and supportively.\n"
    "Do not use brackets, narration, or break character.\n\n"
    f"{context}\n\n"
    f"Customer: {user_msg}\n"
    f"Assistant:"
    )
    
    payload = {
        "model": "MythoMax-L2-13B.Q4_K_M.gguf",
        "prompt": full_prompt,
        "temperature": 0.5,
        "max_tokens": 512,
        "stop": ["</s>", "[/INST]", "Customer:"]
    }

    try:
        response = requests.post("http://localhost:11434/completion", json=payload)
        data = response.json()

        print("\n[debug] Raw response from llama-server:\n", data)

        # Try the common key; fallback if not present
        return data.get("content", "[error] No 'content' key in result.").strip()


    except requests.RequestException as e:
        return f"[error] Server request failed: {e}"
    except Exception as e:
        return f"[error] Unexpected exception: {e}"
