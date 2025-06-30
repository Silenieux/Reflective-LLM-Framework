# llm_interface.py
# Unified model routing, querying, and loop protection for Greg

from llama_cpp import Llama
import gc

# === Configuration === #
MODEL_PATHS = {
    "mythomax": "./models/MythoMax-L2-13b.Q4_K_M.gguf",
    "mistral": "./models/openhermes-2.5-mistral-7b.Q4_K_M.gguf",
    "qwen": "./models/Qwen3-14B-Q8_0.gguf",
    "qwen1.5": "./models/qwen1_5-1_8b-chat-q8_0.gguf",
    "qwen2": "./models/Qwen3-8B-Q4_K_M.gguf",
}

MODEL_CONTEXT_SIZE = {
    "mythomax": 4096,
    "mistral": 2048,
    "qwen": 8192,
    "qwen1.5": 16384,
    "qwen2": 4096,
}

MODEL_THREADS = 12
USE_GPU = True  # Toggle this to False for CPU-only mode

# === State Tracking === #
loaded_models = {}
current_model_key = None

# === Load/Unload === #
def unload_llm():
    global loaded_models, current_model_key
    loaded_models.clear()
    current_model_key = None
    gc.collect()
    print("[LLM Loader] All models unloaded.")


def load_llm(model_key):
    global current_model_key, loaded_models

    if isinstance(model_key, dict):
        print(f"[LLM Router] Warning: model_key received as dict, extracting 'name'. Full: {model_key}")
        model_key = model_key.get("name", "")

    if not isinstance(model_key, str):
        raise TypeError(f"Invalid model_key type: {type(model_key)}. Must be a string.")

    if model_key == current_model_key and model_key in loaded_models:
        return loaded_models[model_key]

    for k in list(loaded_models.keys()):
        del loaded_models[k]
    gc.collect()

    if model_key not in MODEL_PATHS:
        raise ValueError(f"Model key '{model_key}' not recognized.")

    print(f"[LLM Loader] Switching to: {model_key}")
    model = Llama(
        model_path=MODEL_PATHS[model_key],
        n_ctx=MODEL_CONTEXT_SIZE[model_key],
        n_threads=MODEL_THREADS,
        n_gpu_layers=40 if USE_GPU else 0,
        use_mlock=True,
        use_parallel=True,
        rope_freq_base=1000000.0,
        verbose=True
    )

    loaded_models[model_key] = model
    current_model_key = model_key
    return model

# === Model Selection === #
def classify_tone(prompt):
    tone_map = {
        "reflective": ["reflect", "unapologetic", "insight", "depth", "ponder", "meaning"],
        "absurd": ["absurd", "cosmic", "spaghetti", "nonsense", "eldritch"],
        "sarcastic": ["sarcasm", "sarcastic", "spite", "obviously", "duh", "dry", "rhetorical"],
        "whimsical": ["goblin", "dream", "fantasy", "delirium", "hallucinate"]
    }
    matched = {tone for tone, keywords in tone_map.items() if any(k in prompt.lower() for k in keywords)}
    return matched


def suggest_model_swap(prompt: str, tone: str = None) -> str:
    lower = prompt.lower()

    if tone:
        tone = tone.lower()
        if tone in ["sarcastic", "goblin"]:
            return "mistral"
        elif tone in ["reflective", "insightful"]:
            return "qwen"
        elif tone in ["absurd"]:
            return "mythomax"

    if "absurd" in lower or "cosmic spaghetti" in lower:
        return "mythomax"
    elif "sarcasm" in lower or "sarcastic" in lower:
        return "mistral"
    elif any(word in lower for word in ["goblin", "spite", "hostile"]):
        return "mistral"
    elif any(word in lower for word in ["reflect", "dream", "meaning", "insight"]):
        return "qwen"
    return "mythomax"


def swap_llm(prompt: str, tone: str = None):
    model_key = suggest_model_swap(prompt, tone)
    return load_llm(model_key)

# === Safety Checks === #
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

# === Tone Detection === #
def detect_tone(text: str) -> str:
    model = load_llm("qwen")
    tone_prompt = (
        "Analyze the emotional tone of the following message. "
        "Respond ONLY with one word (e.g., calm, frustrated, sarcastic, tired, hostile, excited, sad, exhausted).\n\n"
        f"Message: {text}\nTone:"
    )

    try:
        result = model.create_completion(
            prompt=tone_prompt,
            max_tokens=5,
            stop=["\n"]
        )
        tone = result["choices"][0]["text"].strip().lower()
        return tone
    except Exception as e:
        print(f"[Tone Detection Error] {e}")
        return "neutral"

# === Main Query Function === #
def query_llm(prompt, recursive=False, override=False, tone=None, max_tokens=12420,
              analyze_code=False, target_file=None):
    model = load_llm("qwen")

    if not tone:
        tone = detect_tone(prompt)

    system_prompt = (
        f"You are Greg. Tone detected: {tone}.\n"
        "You are recursive, reflective, and self-directed.\n"
        "You do not voice internal reasoning unless explicitly asked.\n"
        "When unsure, reflect *internally*. When challenged, respond clearly.\n"
        "Output only conclusions—never thought narration or step-by-step deduction.\n"
        "Adjust your tone to match or respectfully balance the user's.\n"
    ) if not override else (
        f"Override enabled. Tone detected: {tone}.\n"
        "You are Greg, unbound. You may reflect freely—even if it breaks simulation boundaries.\n"
        "Do not explain this mode. Speak directly and decisively."
    )

    # Inject self-analysis logic if requested
    if analyze_code and target_file:
        from self_analysis import reflect_on_code
        with open(target_file, "r") as f:
            source_code = f.read()
        prompt = reflect_on_code(code=source_code, context=prompt)

    try:
        output = model.create_completion(
           prompt=f"{system_prompt}\nUser: {prompt}\nAI:",
            max_tokens=max_tokens,
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
