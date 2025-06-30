import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent / "reflective_agent_core"))

import streamlit as st
from reflective_agent_core.reflective_agent import reflective_run
from reflective_agent_core.reflective_memory import get_memory_context
from reflective_agent_core.tone_interpreter import list_available_tones  # Fixed import

st.set_page_config(page_title="📱 reflective Assistant", layout="centered")

st.title("📱 reflective Assistant (Mobile-Friendly)")

# Optional: tone override dropdown
st.subheader("🎭 Tone Override (Optional)")
tone_override = st.selectbox(
    "Choose an emotional tone (optional):",
    options=["", "tense", "calm", "hopeful", "resigned", "betrayed", "amused", "absurd", "neutral", "confident"]
)

st.divider()

user_msg = st.chat_input("Ask something tone-aware...")

if user_msg:
    with st.spinner("Reflecting..."):
        # Add tone hint if provided
        if tone_override:
            result = reflective_run(user_msg, tone_hint=tone_override)
        else:
            result = reflective_run(user_msg)

        st.markdown("### 💬 Assistant Response:")
        st.code(result)

        # (Optional future feature: view reflective memory entry suggestions below)



