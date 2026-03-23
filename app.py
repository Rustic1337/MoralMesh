import streamlit as st
import google.generativeai as genai
import time
from google.api_core.exceptions import ResourceExhausted

st.set_page_config(page_title="EthicsBot – EE Ethics", page_icon="⚡", layout="wide")

# ── Helper functions ─────────────────────────────────────────
def build_history(messages):
    if len(messages) <= 6:
        return messages[:-1]

    recent = messages[-3:-1]

    summary = "Summary of previous conversation:\n"
    for m in messages[:-3]:
        summary += f"{m['role']}: {m['content'][:100]}\n"

    return [{"role": "user", "content": summary}] + recent


def safe_send(chat, msg):
    for _ in range(3):
        try:
            return chat.send_message(msg)
        except ResourceExhausted:
            time.sleep(2)
    return None


# ── Gemini response (FINAL FIXED) ────────────────────────────
def get_gemini_response(messages, system_prompt):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

    # 🔥 Try multiple models (fallback system)
    model_names = [
        "gemini-1.5-flash",
        "models/gemini-1.5-flash",
        "gemini-pro"
    ]

    for name in model_names:
        try:
            model = genai.GenerativeModel(
                model_name=name,
                system_instruction=system_prompt
            )

            history = []
            for m in build_history(messages):
                role = "user" if m["role"] == "user" else "model"
                history.append({"role": role, "parts": [m["content"]]})

            chat = model.start_chat(history=history)

            response = safe_send(chat, messages[-1]["content"])

            if response:
                return response.text

        except Exception:
            continue  # try next model

    return "⚠️ API/model issue. Check your API key or try again later."


# ── Session state ────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_call" not in st.session_state:
    st.session_state.last_call = 0
if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""


# ── Display previous messages ────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ── Chat input ───────────────────────────────────────────────
if prompt := st.chat_input("Ask about engineering ethics, IEEE codes, Pakistan cases…"):

    # ⏳ Cooldown
    now = time.time()
    if now - st.session_state.last_call < 2:
        st.warning("⏳ Wait a second before sending another message")
        st.stop()

    st.session_state.last_call = now

    # 🚫 Prevent duplicate calls
    if prompt == st.session_state.last_user_input:
        st.stop()

    st.session_state.last_user_input = prompt

    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = get_gemini_response(
                st.session_state.messages,
                "You are an expert Electrical Engineering Ethics assistant. Give structured, clear, academic answers."
            )

        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
