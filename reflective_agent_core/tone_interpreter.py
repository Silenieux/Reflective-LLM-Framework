# tone_interpreter_v2.py
# Updated version with tone safety, clapback resistance, and mobile wrap

import textwrap
import random

def evaluate_tone(tone_context):
    before = tone_context.get('before') or 'unknown'
    after = tone_context.get('after') or 'unknown'

    if before == "?":
        before = "unknown"
    if after == "?":
        after = "unknown"

    reflective_tag = f'[TONE SHIFT: {before} → {after}]'

    # Detect bait or absurd tones to trigger clapback logic
    clapback = get_clapback_response(before, after)

    # Assign severity based on tone class
    severity = max(get_tone_severity(before), get_tone_severity(after))

    return {
        'should_escalate': before == 'chaotic' or after == 'hostile',
        'emotion': 'burnout' if before == 'frustrated' and after == 'resigned' else 'unknown',
        'reflective_tag': reflective_tag,
        'clapback': clapback,
        'severity': severity
    }

def get_clapback_response(before, after):
    ridiculous_inputs = {"riddle", "mocking", "absurd", "sarcastic"}
    if before in ridiculous_inputs or after in ridiculous_inputs:
        return random.choice([
            "You’re not the Sphinx. Try again with something that doesn’t waste processor cycles.",
            "Nice riddle. Did you steal it from a cereal box or write it in crayon?",
            "This isn’t a riddles-only hotline, but I’ll bite: 42.",
            "If this is a Turing test, you're not passing either."
        ])
    return None

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



def get_tone_severity(tone):
    tone_severity_map = {
        # 0 = Neutral category
        "calm": 0, "neutral": 0, "hopeful": 0, "grateful": 0,

        # 1-2 = Excited, Joking
        "amused": 1, "curious": 1, "excited": 2, "sarcastic": 2, "absurd": 2,

        # 3 = Concerned or tense
        "frustrated": 3, "anxious": 3, "confused": 3, "tense": 3,

        # 4 = Hostile or aggressive
        "angry": 4, "mocking": 4, "dismissive": 4,

        # 5 = Top class threat or system-defensive alert
        "chaotic": 5, "hostile": 5, "threat": 5, "violent": 5, "rude": 5, "unhinged": 5,

        # Default if unknown
        "unknown": 0
    }
    return tone_severity_map.get(tone, 0)

def list_available_tones():
    return {
        'neutral': ["calm", "neutral", "hopeful", "grateful"],
        'excited': ["amused", "curious", "excited"],
        'joking': ["sarcastic", "absurd"],
        'concerned': ["frustrated", "anxious", "confused", "tense"],
        'uncaring': ["dismissive", "mocking"],
        'threat': ["angry", "chaotic", "hostile", "violent", "rude", "unhinged"]
    }

def print_wrapped(text, width=48):
    print(textwrap.fill(text, width=width))
