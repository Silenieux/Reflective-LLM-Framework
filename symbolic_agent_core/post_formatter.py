import textwrap
import random

def format_post(response, tone_meta, tags, width=80):
    before = tone_meta.get('before', '?')
    after = tone_meta.get('after', '?')

    # 🛠 Absurd tone fallback correction
    if before == "?" and after == "?" and "absurd-response" in tags:
        before = "absurd"
        after = "amused"

    # ✨ Stylized reflection variants
    if "absurd-response" in tags:
        alt_reflections = [
            "That’s certainly one for the books! Can you clarify what you'd like me to help with?",
            "Wow, that’s a new one! Let's figure out how I can assist anyway.",
            "Fascinating... Let’s redirect our energy toward something a little more helpful.",
            "You win the creativity prize. What’s the real issue you need help with today?"
        ]
        response = random.choice(alt_reflections)

    # 🎭 Symbolic tag and response
    symbolic_tag = f"[TONE SHIFT: {before} → {after}]"
    tag_line = " ".join(f"#{tag}" for tag in tags)
    wrapped_response = textwrap.fill(response, width=width)

    # 🌀 Outcome variants for absurdities
    if "absurd-response" in tags:
        outcome = random.choice([
            "Tone softened. Engagement warped into whimsy. Reality barely survived.",
            "Tone refracted through absurdity. Laughter increased. No one was harmed.",
            "Tone shift successful. Cognitive dissonance reduced by 82%.",
            "Tone stabilized. Situation redirected. Giraffes unbothered."
        ])
    else:
        outcome = "Tone softened. Engagement increased. Chaos avoided."

    return f"""
🎭 {symbolic_tag}
🎯 [TAGS: {tag_line}]

🧠 Reflection:
{wrapped_response}

💬 Agent Thought:
This seemed like a chance to shift tone with symbolic empathy and targeted deflection.

✅ Symbolic Outcome:
{outcome}
""".strip()
