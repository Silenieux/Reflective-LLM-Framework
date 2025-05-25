# Final demo-safe symbolic assistant with fallback and redaction

import sys
import re
from pathlib import Path
import importlib.util
import streamlit as st

core_path = Path(__file__).resolve().parent / "core_logic"
sys.path.append(str(core_path))

spec = importlib.util.spec_from_file_location("tone_interpreter", core_path / "tone_interpreter.py")
tone_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tone_module)
evaluate_tone = tone_module.evaluate_tone

from symbolic_responder import load_symbolic_memory, generate_symbolic_reply
llm_runner_path = core_path / "local_llm_runner.py"
llm_spec = importlib.util.spec_from_file_location("local_llm_runner", llm_runner_path)
llm_module = importlib.util.module_from_spec(llm_spec)
llm_spec.loader.exec_module(llm_module)
reflect_locally = llm_module.reflect_locally

def answer_factually(user_msg):
    prompt = f"""
You are a helpful assistant. Answer factually and clearly.
If you mention listing examples or steps, follow through with bullet points or numbered responses.
Use the question context to stay on-topic.

Context: {st.session_state.get('raw_input', user_msg)}
Question: {user_msg}
Answer:
"""
    response = llm_module.llm(prompt, max_tokens=256, stop=["\n"])
    return response["choices"][0]["text"].strip()

def break_down_questions(user_msg):
    parts = re.split(r'(\?\s+|\band\b|\bor\b)', user_msg)
    chunks = []
    current = ''
    for part in parts:
        current += part
        if '?' in part or len(current) > 80:
            chunks.append(current.strip())
            current = ''
    if current:
        chunks.append(current.strip())
    return [q for q in chunks if len(q) > 4]

def redact_sensitive_info(text):
    return re.sub(r"(?i)\b(home address|phone number|social security|password|secret|account)\b", "[REDACTED]", text)

st.set_page_config(page_title="📱 Symbolic Assistant", layout="centered")
st.title("📱 Symbolic Assistant (Final Demo Build)")

st.subheader("🎭 Tone Override (Optional)")
tone_override = st.selectbox(
    "Choose an emotional tone (optional):",
    options=["", "tense", "calm", "hopeful", "resigned", "betrayed", "amused", "absurd", "neutral", "confident"]
)

st.divider()

use_llm = st.checkbox("🧠 Enable live reflection (LLM)", value=False)

user_msg = st.chat_input("Ask something tone-aware (or multi-part)...")

if user_msg:
    with st.spinner("Reflecting..."):
        st.session_state['raw_input'] = user_msg
        user_msg = redact_sensitive_info(user_msg)
        default_tone = tone_override if tone_override else "neutral"
        tone_context = {"before": "neutral", "after": default_tone}
        tone_meta = evaluate_tone(tone_context)

        symbolic_tag = tone_meta.get("symbolic_tag", "[TONE SHIFT: unknown → unknown]")
        memory_path = Path(__file__).resolve().parent / "memory" / "symbolic_memory_seed.json"
        memory_db = load_symbolic_memory(str(memory_path))

        questions = break_down_questions(user_msg)
        symbolic_output = ""

        for q in questions:
            if use_llm:
                part = reflect_locally(q, tone_context) or ""
                if "used_clapbacks" not in st.session_state:
                    st.session_state.used_clapbacks = []
                if part in st.session_state.used_clapbacks:
                    part = "[Repeated symbolic clapback suppressed.]"
                else:
                    st.session_state.used_clapbacks.append(part)

                if not part or not part.strip() or part.lower().strip() in ["[repeated symbolic clapback suppressed.]", ""] or len(part.strip()) < 5:
                    part = answer_factually(q)
            else:
                part = generate_symbolic_reply(tone_context["before"], memory_db)
                if not part.strip():
                    part = answer_factually(q)

            symbolic_output += f"- {q}\n{part}\n\n"

        result = f"{symbolic_tag}\n{symbolic_output}"

        st.text_area("🗣️ User Message", user_msg, height=80, disabled=True)
        st.text_area("💬 Assistant Response", result, height=200, disabled=True)

        if "last_saved" not in st.session_state:
            st.session_state.last_saved = None

        if st.button("💾 Save to symbolic memory") and st.session_state.last_saved != user_msg:
            from datetime import datetime
            import json

            new_entry = {
                "Title": "Auto-Logged Interaction",
                "Summary": st.session_state.get('raw_input', user_msg),
                "Reflective Prompt": f"What can be learned from this shift: {tone_context['before']} → {tone_context['after']}?",
                "Bias Tags": ["auto-logged", "live-interaction", "symbolic-ui"],
                "Memory Type": "reflective",
                "Continuity Cue": "User Query",
                "Reflection Status": "pending",
                "tone_context": tone_context,
                "timestamp": datetime.now().isoformat()
            }

            try:
                with open(memory_path, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
                memory_data.append(new_entry)
                with open(memory_path, 'w', encoding='utf-8') as f:
                    json.dump(memory_data, f, indent=2)
                st.success("✅ Interaction saved to symbolic memory!")
                st.session_state.last_saved = user_msg
            except Exception as e:
                st.error(f"❌ Failed to save memory: {e}")

