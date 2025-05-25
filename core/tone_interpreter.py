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

    symbolic_tag = f'[TONE SHIFT: {before} → {after}]'

    # Detect bait or absurd tones to trigger clapback logic
    clapback = get_clapback_response(before, after)

    return {
        'should_escalate': before == 'chaotic' or after == 'hostile',
        'emotion': 'burnout' if before == 'frustrated' and after == 'resigned' else 'unknown',
        'symbolic_tag': symbolic_tag,
        'clapback': clapback
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

def list_available_tones():
    return [
        "angry", "calm", "frustrated", "resigned", "chaotic", "neutral",
        "amused", "absurd", "curious", "hopeful", "grateful", "tense", "mocking", "hostile",
        "confused", "anxious", "dismissive", "sarcastic"
    ]

def print_wrapped(text, width=48):
    print(textwrap.fill(text, width=width))
