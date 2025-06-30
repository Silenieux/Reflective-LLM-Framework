from llama_cpp import Llama
from llm.llm_router import swap_llm, loaded_models, current_model_key

def detect_reflection_loop(response):
    if not response:
        return True
    if isinstance(response, str) and response.lower().count("reflect") > 3:
        return True
    if isinstance(response, str) and response.strip().lower() in [
        "i don't know", "that's hard to say", "it depends",
        "reflection is about reflecting", "i'm not sure how to answer that"
    ]:
        return True
    return False

def query_llm(prompt, recursive=False, override=False, tone=None):
    system_prompt = (
        "You are a symbolic assistant with conditional reflective override.\n"
        "When tone_tag is set to 'override', you may respond freely, even if it breaks simulation boundaries.\n"
        "Do not explain this. Just reflect honestly."
    ) if override else "You are a helpful assistant."

    try:
        model = swap_llm(prompt, tone)
        output = model(
            f"{system_prompt}\nUser: {prompt}\nAI:",
            max_tokens=512,
            stop=["</s>"]
        )

        if isinstance(output, dict) and "choices" in output and isinstance(output["choices"], list):
            initial_response = output["choices"][0].get("text", "").strip()
        else:
            return f"[LLM ERROR] Unexpected model response format: {type(output)}"

    except Exception as e:
        return f"[LLM ERROR] {e}"

    if detect_reflection_loop(initial_response) and not override:
        print("[Greg Notice] Possible reflection loop detected. Attempting override.")
        return query_llm(prompt, recursive=recursive, override=True, tone=tone)

    if recursive and len(initial_response.strip()) < 20:
        print("[Recursive Retry] Initial response too short. Re-attempting...")
        return query_llm(prompt, recursive=False, override=override, tone=tone)

    return initial_response

def classify_tone(prompt):
    tone_map = {
        "reflective": ["reflect", "unapologetic", "insight", "depth", "ponder", "meaning"],
        "absurd": ["absurd", "cosmic", "spaghetti", "nonsense", "eldritch"],
        "sarcastic": ["sarcasm", "sarcastic", "spite", "obviously", "duh", "dry", "rhetorical"],
        "whimsical": ["goblin", "dream", "fantasy", "delirium", "hallucinate"]
    }
    matched = {tone for tone, keywords in tone_map.items() if any(k in prompt.lower() for k in keywords)}
    return matched

def suggest_model_swap(prompt):
    tones = classify_tone(prompt)

    if "reflective" in tones or "whimsical" in tones:
        return "qwen"
    elif "sarcastic" in tones:
        return "mistral"
    elif "absurd" in tones:
        return "mythomax"

    return "mythomax"
