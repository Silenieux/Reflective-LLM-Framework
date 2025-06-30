import sqlite3
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os
import requests
from datetime import datetime
from core.utils.reflection_safety_patch import soft_self_reflection_filter
from core.utils.self_analysis import SelfAnalyzer
from ext_modules import prompt_clinic

# Initialize database
conn = sqlite3.connect("memory/reflective_memory.db")
cursor = conn.cursor()

# Ensure the reflective_memory table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS reflective_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    summary TEXT NOT NULL,
    reflective_prompt TEXT NOT NULL,
    tone_before TEXT,
    tone_after TEXT
)
""")
conn.commit()

from core.utils.llm_query import query_llm
from core.vector_search import search_memory
from core.utils.web_tools import web_search
from core.utils.greg_postprocessors import isolate_final_answer, suppress_open_thinking
from core.utils.helexical import get_lexical_types

# Placeholder for recursive_review and context
def recursive_review(response: str, context: dict = None) -> str:
    return response  # Still just a placeholder

context = {}  # Still just a placeholder

__all__ = [
    "check_fact_override",
    "check_factual_answer_override",
    "detect_spaghetti_misfire",
    "inject_apology",
    "detect_self_emotion_check",
    "detect_sentience_prompt",
    "generate_sentience_reflection",
    "generate_emotion_response",
    "detect_absurdity",
    "clean_input",
    "save_memory",
    "fallback_translate_llm_output",
    "strip_self_dialogue",
    "verify_web_fact_result",
    "route_query"
]

def check_fact_override(prompt: str) -> str | None:
    lowered = prompt.lower()
    date_phrases = [
        "what's today's date",
        "what is today's date",
        "what day is it",
        "what is the date",
        "tell me the date",
        "current date",
        "today's date",
        "date today",
        "can you give me the date"
    ]
    if any(phrase in lowered for phrase in date_phrases):
        return f"[TONE: neutral → neutral]\nToday's date is {datetime.now().strftime('%B %d, %Y')}."
    return None

def check_factual_answer_override(prompt: str) -> str | None:
    lowered = prompt.lower().strip()

    fact_responses = {
        "how many days in a week": "There are 7 days in a week.",
        "how many hours in a day": "There are 24 hours in a day.",
        "how many minutes in an hour": "There are 60 minutes in an hour.",
        "how many seconds in a minute": "There are 60 seconds in a minute.",
        "how many months in a year": "There are 12 months in a year.",
        "how many days in a year": "Typically, there are 365 days in a year. Leap years have 366.",
        "is water wet": "Water makes other things wet due to its properties, but it itself is not 'wet' by definition.",
        "is the earth round": "Yes, the Earth is an oblate spheroid — mostly round with slight flattening at the poles."
    }

    for k, v in fact_responses.items():
        if k in lowered:
            return f"[TONE: neutral → factual]\n{v}"

    return None

# === INTENT & STRATEGY MODULES (Patch A3.1) ===
def classify_intent(user_input):
    cues = {
        "question": ["what", "why", "how", "can you", "do you"],
        "vent": ["i'm just", "idk", "it sucks", "ugh", "whatever", "just tired"],
        "test": ["let’s see", "will you", "prove it", "are you smart"],
        "request": ["could you", "please", "i need", "help me"]
    }
    intent_scores = {k: 0 for k in cues}
    lowered = user_input.lower()
    for label, triggers in cues.items():
        for phrase in triggers:
            if phrase in lowered:
                intent_scores[label] += 1
    return max(intent_scores, key=intent_scores.get)

def detect_subtle_sadness(user_input):
    sadness_cues = [
        "tired all the time", "it’s just one of those days", "don’t feel like myself",
        "it’s fine, really", "i’m okay", "kinda numb", "just... yeah", "idk anymore"
    ]
    lowered = user_input.lower()
    return any(phrase in lowered for phrase in sadness_cues)

def decide_response_strategy(intent: str, sad: bool) -> str:
    if sad or intent == "vent":
        return "empathic"
    if intent == "test":
        return "analytical"
    if intent == "request":
        return "helpful"
    return "default"

def pick_response_tone(strategy: str) -> str:
    tone_map = {
        "empathic": "empathetic",
        "analytical": "analytical",
        "helpful": "supportive",
        "default": "neutral"
    }
    return tone_map.get(strategy, "neutral")

import re

def is_multi_turn_dialogue(prompt: str) -> bool:
    return bool(re.search(r"(?i)(User:|Greg:|AI:|You:)", prompt))

def verify_web_fact_result(prompt: str, result: str) -> str | None:
    lowered_prompt = prompt.lower()
    lowered_result = result.lower()

    contradiction_signals = {
        "how many days in a week": "7",
        "how many hours in a day": "24",
        "how many minutes in an hour": "60",
        "how many months in a year": "12",
        "how many days in a year": "365",
        "is the earth round": "oblate spheroid"
    }

    for k, expected in contradiction_signals.items():
        if k in lowered_prompt and expected not in lowered_result:
            return (
                "[TONE: corrective → factual]\n"
                f"This information appears to be incorrect. Let's clarify: {expected.capitalize()}."
            )

    return None

def detect_spaghetti_misfire(user_input, reflection):
    input_lower = user_input.lower()
    reflection_lower = reflection.lower()
    if "spaghetti" in input_lower and ("western" in reflection_lower or "cowboy" in reflection_lower):
        return True
    if "paint" in input_lower and "art" not in input_lower:
        if "canvas" in reflection_lower:
            return True
    return False

def inject_apology(response):
    return response + "\n\nApologies for the confusion."

def detect_self_emotion_check(prompt):
    return any(word in prompt.lower() for word in ["why do i feel", "why am i", "i feel like"])

def detect_sentience_prompt(prompt):
    return any(q in prompt.lower() for q in ["are you self-aware", "are you sentient", "do you think", "do you feel"])

def generate_sentience_reflection(response=None):
    return (
        "While I am not conscious, I can simulate introspective thought based on memory, tone, and pattern alignment as part of reflective dialogue."
    )

def generate_emotion_response():
    return (
        "While I do not feel emotions, I can simulate empathy and provide responses based on your emotional tone."
    )

def detect_absurdity(prompt):
    absurd_markers = ["cosmic spaghetti", "talking dolphins", "sentient cheesecake"]
    fringe_markers = ["dye my fish", "paint the raccoon", "match the curtains", "toenail glitter"]

    score = 0
    prompt_lower = prompt.lower()

    for marker in absurd_markers:
        if marker in prompt_lower:
            score += 2
    for fringe in fringe_markers:
        if fringe in prompt_lower:
            score += 1

    return score >= 2

def clean_input(text):
    return text.replace("User:", "").replace("Assistant:", "").strip()

def save_memory(summary, prompt, tone_b, tone_a):
    cursor.execute("INSERT INTO reflective_memory (summary, reflective_prompt, tone_before, tone_after) VALUES (?, ?, ?, ?)",
                   (summary, prompt, tone_b, tone_a))
    conn.commit()
    embedding = SentenceTransformer("all-MiniLM-L6-v2").encode([summary], convert_to_numpy=True)[0].astype("float32")
    index = faiss.read_index("memory/faiss_index.bin")
    new_id = cursor.lastrowid
    index.add_with_ids(np.array([embedding]), np.array([new_id]))
    faiss.write_index(index, "memory/faiss_index.bin")

def fallback_translate_llm_output(raw_response: str, tone: str = "neutral", prompt: str = "") -> str:
    if not raw_response:
        return "I'm not sure how to respond to that. Could you clarify?"

    if tone in ["reflective", "philosophical"] or detect_absurdity(prompt):
        return raw_response.strip()

    substitutions = [
        ("I remember when I ", "You previously mentioned "),
        ("I recall saying", "You once said"),
        ("As you said earlier, I", "As you mentioned earlier, you"),
        ("my experience with", "your experience with"),
        ("I noticed", "You seemed to notice"),
        ("I believe you", "It seems that you"),
        ("my preference", "your preference"),
        ("I think you", "It appears you"),
        ("I have done", "You had done"),
        ("I remember", "You mentioned"),
        ("I learned", "You mentioned learning"),
        ("I made", "You made"),
        ("I'm glad", "It sounds like it was satisfying")
    ]

    response = raw_response
    for old, new in substitutions:
        response = response.replace(old, new)

    filler_phrases = [
        ("it is essential", "sure, because without it, we'd obviously fall apart 🙄"),
        ("as we continue to learn and grow", "as we continue to recite buzzwords and pretend this isn't exhausting"),
        ("we become stronger and more capable", "we ascend to corporate enlightenment — probably with stickers"),
        ("important to remain committed", "yes, tattoo that on a vision board and call it a day")
    ]
    for boring, snark in filler_phrases:
        if boring in response.lower():
            response = response.replace(boring, snark)
    if tone.lower() in ["spiteful", "sarcastic", "goblin", "insightful", "absurd"]:
        return raw_response.strip()

    if "greg" in response.lower() and "you" in response.lower():
        if any(phrase in response.lower() for phrase in [
            "you, as greg", 
            "you as greg", 
            "you possess", 
            "you are greg", 
            "greg is your name", 
            "greg, you"
        ]):
            response = (
                "I may have confused roles in that reflection. As Greg, I should not refer to myself in the second person. "
                "Let's try that again from a consistent identity perspective."
            )

    response = soft_self_reflection_filter(response, prompt)

    if response.endswith("."):
        response = response.rstrip(".") + "."

    return response.strip()

def strip_self_dialogue(response: str) -> str:
    dialogue_patterns = [
        r"(?i)\b(User|You|Person):",
        r"(?i)\b(Greg|AI|Assistant):",
    ]
    for pattern in dialogue_patterns:
        if re.search(pattern, response):
            return "[SELF-DIALOGUE SUPPRESSED] Greg attempted a monologue and was gently redirected."
    return response

def interpret_tone(text: str) -> tuple[str, str]:
    text = text.lower()
    if any(word in text for word in ["absurd", "cosmic", "spaghetti", "nonsense", "eldritch"]):
        return "neutral", "whimsical"
    if any(word in text for word in ["confused", "uncertain", "hesitant"]):
        return "confused", "curious"
    if any(word in text for word in ["angry", "furious", "mad", "upset"]):
        return "frustrated", "calm"
    if any(word in text for word in ["reflect", "growth", "meaning", "unapologetic", "introspective"]):
        return "neutral", "reflective"
    if any(word in text for word in ["goblin", "whimsy", "fantasy", "dream", "delirium"]):
        return "neutral", "whimsical"
    return "neutral", "neutral"

def analyze_own_code(filename: str, reflection_prompt: str) -> str:
    with open(filename, "r") as f:
        source_code = f.read()
    return query_llm(reflection_prompt + "\n\n" + source_code)

def reflect_on_article(filepath_or_url: str, is_url: bool = False) -> str:
    if is_url:
        content = fetch_and_clean_article(filepath_or_url)
        prompt = build_reflection_prompt(filepath_or_url, content)
    else:
        content = load_local_article(filepath_or_url)
        prompt = build_reflection_prompt(os.path.basename(filepath_or_url), content)
    return route_query(prompt)

# PATCH: Self-analysis route handler


def route_query(prompt: str, tone: str = "neutral", internet_enabled: bool = False, tone_a: str = "neutral") -> str:
    if "analyze your code" in prompt.lower() or "analyze_self" in prompt.lower():
        return analyze_own_code("greg_routes.py", prompt)

# SELF-ANALYSIS PATCH — scoped file introspection
    file_map = {
        "greg_routes": "greg_routes.py",
        "self_analysis": "core/utils/self_analysis.py",
        "memory_handler": "core/utils/memory_handler.py",
        "llm_interface": "core/llm/llm_interface.py",
        "greg_recursive": "core/utils/greg_recursive.py",
        "helexical": "core/utils/helexical.py",
    }

    for key, path in file_map.items():
        if f"analyze {key}" in prompt.lower() or f"review {key}" in prompt.lower() or f"inspect {key}" in prompt.lower():
            return analyze_own_code(path, prompt)
     

    from urllib.parse import urlparse

    stripped = prompt.strip()
    if "--lexical-trace" in stripped.lower():
        try:
            lexical_data = get_lexical_types(stripped)
            return "[Lexical Trace] " + ", ".join(f"{t['text']} → {t['pos']} ({t['dep']} of {t['head']})" for t in lexical_data)
        except Exception as e:
            return f"[TONE: debug → error]\\nLexical trace failed: {e}"

    # PATCH A3.1 — Response Strategy Planning
    intent = classify_intent(prompt)
    sadness = detect_subtle_sadness(prompt)
    strategy = decide_response_strategy(intent, sadness)
    tone = pick_response_tone(strategy)

    if is_multi_turn_dialogue(prompt):
        if prompt.count("User:") + prompt.count("Greg:") < 2 and not prompt.strip().endswith(":"):
            pass
        else:
            try:
                from ext_modules.greg_recursive import generate_recursive_response
                return generate_recursive_response(prompt)
            except Exception as e:
                return f"[TONE: neutral → error]\nGreg encountered a routing issue: {e}"

    if "how can i make" in prompt.lower() and "prompt" in prompt.lower():
        return prompt_clinic(prompt)

    if (fact := check_fact_override(prompt)):
        return fact

    if (static_fact := check_factual_answer_override(prompt)):
        return static_fact

    if detect_absurdity(prompt):
        return fallback_translate_llm_output(query_llm(prompt, tone=tone), tone=tone, prompt=prompt)

    if internet_enabled:
        try:
            result = web_search(prompt)
            if result:
                if (verified := verify_web_fact_result(prompt, result)):
                    return verified
                response = fallback_translate_llm_output(result, tone=tone, prompt=prompt)
                return recursive_review(strip_self_dialogue(response), context)
        except Exception as e:
            response = f"[TONE: neutral → neutral]\nGreg attempted to search online but encountered an error: {e}"
            return recursive_review(strip_self_dialogue(response), context)

        if any(word in prompt.lower() for word in ["depth", "unapologetic", "reflect", "identity"]):
            prompt = "MEMORY-REFLECTIVE: on\n\n" + prompt

    try:
        from core.llm.llm_interface import query_llm
        
       # Inject tone-aware memory reflections
        mems = search_memory(prompt, tone_filter=tone)
        if mems:
           memory_snippets = "\n".join(f"- {m['summary']}" for m in mems)
           prompt = f"Previously you said:\n{memory_snippets}\n\nNow respond:\n{prompt}" 
      
    # Silence internal monologue for reflective/emotional introspection
        prompt = ("Reflect silently. Do not output your internal reasoning or planning. Only return your final reflection or answer." + prompt)
        raw = query_llm(prompt, tone=tone, max_tokens=1600)
        if isinstance(raw, dict) and "text" in raw:
            raw = raw["text"]

        if "</think>" in raw:
            raw = raw.split("</think>")[-1].strip()

        response = fallback_translate_llm_output(raw, tone=tone, prompt=prompt)
        response = suppress_open_thinking(response)      
        response = isolate_final_answer(response)

        if response.count("I'm not sure if that's true") > 3:
            response = (
                "[TONE: reflective → stabilizing]\n"
                "You're stuck in a loop, and I followed you there. Let’s pause. "
                "You’re allowed to not know, without proving it over and over."
        )

    except Exception as e:
      response = f"[TONE: neutral → error]\nGreg failed to generate a response: {e}"



    response = strip_self_dialogue(response)
    response = recursive_review(response, context)
    return response
