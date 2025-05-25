def build_fallback_prompt(context_block, customer_message, tone_hint=None):
    instruction = (
        "You are a helpful support assistant who also understands humor and urgency. "
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
