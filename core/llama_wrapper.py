
from llama_cpp import Llama

def generate_response(context_block, user_msg, model_path):
    model = Llama(
        model_path=model_path,
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
