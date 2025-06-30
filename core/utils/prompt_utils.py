def build_fallback_prompt(context_block, customer_message, tone_hint=None):
    instruction = (
        "You are a helpful support assistant who also understands humor, sarcasm, and urgency. "
        "Keep the tone light, but informative. If the situation sounds silly, play along."
    )

    prompt = f"""
{instruction}

[KNOWLEDGE=ToneRecall]
{context_block.strip()}

[CUSTOMER MESSAGE]
{customer_message.strip()}

[ASSISTANT REPLY]
"""
    if tone_hint:
        prompt += f"(Tone: {tone_hint})\n"
    return prompt.strip()
def needs_reflection(response: str, context: dict) -> bool:
    # Simple heuristic: tone mismatch, fallback keyword, or contradiction marker
    drift_signals = ["[FALLBACK]", "[TONE: mismatch]", "contradiction detected", "inconsistent"]
    return any(signal in response for signal in drift_signals)

def regenerate_with_reflection(response: str, context: dict) -> str:
    from llm_query import query_llm  # Lazy import to avoid circulars
    prompt = build_reflection_prompt(response, context)
    return query_llm(prompt)

def build_reflection_prompt(response: str, context: dict) -> str:
    return (
        f"Analyze and regenerate the following assistant response while correcting tone or logical drift:\n\n"
        f"Original Response:\n{response}\n\n"
        f"User Context:\n{context.get('user_input', '')}\n\n"
        f"Preserve core message but enhance tone consistency and clarity."
    )




