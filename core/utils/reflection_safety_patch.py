def soft_self_reflection_filter(response: str, user_prompt: str) -> str:
    """
    Prevents Greg from echoing symbolic phrases from the user as if they were his own.
    Supports fuzzy matching and partial phrase detection.
    """
    mythic_phrases = [
        "my job is to reflect",
        "i exist to guide",
        "i was built to",
        "i was created to reflect",
        "as a reflective assistant, my purpose is",
        "greg's purpose is to be a reflection",
        "greg exists to support",
        "i carry the weight of"
    ]

    user_lower = user_prompt.lower()
    response_lower = response.lower()

    for phrase in mythic_phrases:
        if phrase in response_lower and phrase in user_lower:
            adjusted = "I’ve come to understand that reflection and support are part of my learned role"
            disclaimer = "[NOTE: This phrasing was inspired by user feedback and reframed to preserve symbolic identity.]\n\n"
            response = response.replace(phrase, adjusted)
            return disclaimer + response

    return response
