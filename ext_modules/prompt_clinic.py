"""
Prompt Clinic Module v0.2
-------------------------
Analyzes vague or unclear prompts and suggests cleaner, more accurate phrasing.
Also helps identify prompts that may trigger hallucinations in language models.
Designed for use with Greg, your reflective assistant who values clarity over chaos.
Comments are dry and mildly sarcastic—just enough to keep developers awake.
A toggle to enable or disable prompt clinic can be enabled or disabled to act
as a training mode for users that are new to LLM's or need help getting started.
"""

from typing import Dict
import re

try:
    from core.utils.llm_query import query_llm
except ImportError:
    # If Greg's memory got scrambled and forgot where this is.
    query_llm = lambda x: "[LLM fallback unavailable.]"

def analyze_prompt(prompt: str) -> Dict[str, str]:
    ...
    # (same as before — left intact for sass and sarcasm)
    return results

def improve_prompt(prompt: str, use_llm=False) -> str:
    prompt = prompt.strip()
    if not prompt:
        return "[Please enter a complete prompt to improve.]"

    improved = prompt
    improved = re.sub(r"^(can you|could you)\s", "Please ", improved, flags=re.IGNORECASE)
    improved = re.sub(r"\b(just|maybe|kind of|sort of|like)\b", "", improved, flags=re.IGNORECASE)

    if improved and not improved[0].isupper():
        improved = improved[0].upper() + improved[1:]

    if not improved.endswith(('.', '?', '!')):
        improved += '.'

    # If it still looks like a poorly-written cry for help, let the LLM try
    if use_llm and len(improved.strip()) < 12:
        try:
            return query_llm(f"Rewrite this prompt to be clearer: {prompt}")
        except Exception as e:
            return f"[LLM fallback failed: {e}]"

    return improved


# If you’re expecting miracles, sorry. This isn’t magic—it’s regular expressions and judgment.
# For now, this helps you avoid confusing Greg (or any LLM) with fuzzy prompt sludge.

def analyze_prompt(prompt: str) -> Dict[str, str]:
    """
    Analyzes a prompt and provides notes on structure, clarity, and risk of hallucination.
    Looks for vague terms, weak structure, or phrasing that lacks directive clarity.
    """
    results = {}
    prompt = prompt.strip()

    if not prompt:
        results['error'] = "Prompt is empty. LLMs can't read your mind—yet."
        return results

    if len(prompt) < 8:
        results['length'] = f"Prompt is very short ({len(prompt)} characters). This may lead to vague or inaccurate responses."

    if prompt.lower().startswith("can you") or prompt.lower().startswith("could you"):
        results['starter'] = "Soft phrasing detected. Direct instructions improve clarity."

    if re.search(r"(just|maybe|kind of|sort of|like)", prompt, re.IGNORECASE):
        results['vagueness'] = "Vague filler words increase hallucination risk. Try direct action language."

    if prompt[0].islower():
        results['capitalization'] = "Starts with lowercase. This isn't a text to your cat. Capitalize it."

    if not prompt.endswith(('.', '?', '!')):
        results['punctuation'] = "No punctuation found. Proper punctuation helps define intent."

    results['accuracy_tip'] = (
        "Prompts are instructions. Ambiguity leads to hallucinations. Use specific, directive language—even if it feels overly formal."
    )

    return results


def improve_prompt(prompt: str) -> str:
    """
    Rewrites a casual or vague prompt to make it clearer and more effective.
    Designed to reduce hallucination risk and maximize LLM comprehension.
    """
    prompt = prompt.strip()
    if not prompt:
        return "[Please enter a complete prompt to improve.]"

    improved = prompt
    improved = re.sub(r"^(can you|could you)\s", "Please ", improved, flags=re.IGNORECASE)
    improved = re.sub(r"\b(just|maybe|kind of|sort of|like)\b", "", improved, flags=re.IGNORECASE)

    if improved and not improved[0].isupper():
        improved = improved[0].upper() + improved[1:]

    if not improved.endswith(('.', '?', '!')):
        improved += '.'

    return improved


if __name__ == "__main__":
    # Demo input: half a question and half a shrug.
    test_input = "can you maybe help with the code"
    print("Original:", test_input)
    print("--- Diagnosis ---")
    print(analyze_prompt(test_input))
    print("--- Improved Prompt ---")
    print(improve_prompt(test_input))
