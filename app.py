import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions

# ── 1. PAGE & API CONFIG ─────────────────────────────────────
st.set_page_config(page_title="EthicsBot – EE Ethics", page_icon="⚡", layout="wide")

# Move this outside the function to stay connected efficiently
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
else:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets!")

# ── 2. STYLING ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f5f4f0; }
.block-container { padding-top: 1.5rem; }
[data-testid="stChatMessage"] { background: white; border-radius: 12px; border: 1px solid #e2ddd4; margin-bottom: 6px; }
section[data-testid="stSidebar"] { background: #0f1f3d !important; }
section[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
</style>
""", unsafe_allow_html=True)

# ── 3. HEADER & PROMPTS ──────────────────────────────────────
st.markdown("""
<div style="background:#0f1f3d;padding:16px 24px;border-radius:12px;border-bottom:3px solid #c9a84c;margin-bottom:20px">
  <h2 style="color:white;margin:0;font-size:1.25rem">⚡ EthicsBot — Electrical Engineering Ethics</h2>
  <p style="color:#f0d98a;margin:4px 0 0;font-size:0.72rem;letter-spacing:0.08em;text-transform:uppercase">
    IEEE · NSPE · Global &amp; Pakistan Case Studies · Professional Ethics
  </p>
</div>
""", unsafe_allow_html=True)

mode = st.selectbox("Mode", ["💬 General Q&A", "🧠 Quiz Me", "📖 Ethical Scenario", "📝 Exam Prep"], label_visibility="collapsed")

SYSTEM_PROMPTS = {
    "💬 General Q&A": "You are EthicsBot, an expert in IEEE, NSPE, and PEC codes. Focus on academic and professional responses.",
    "🧠 Quiz Me": "Ask one multiple-choice question at a time. Explain the answer afterward.",
    "📖 Ethical Scenario": "Present dilemmas like the Baldia Town Fire or substandard wiring and ask for the student's reaction.",
    "📝 Exam Prep": "Provide concise definitions for terms like Whistleblowing and Conflict of Interest."
}

# ── 4. SESSION STATE ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_mode" not in st.session_state:
    st.session_state.current_mode = mode
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

if st.session_state.current_mode != mode:
    st.session_state.messages = []
    st.session_state.current_mode = mode

# ── 5. RESPONSE HELPER (Rate Limit Protected) ───────────────
def get_gemini_response(messages, system_prompt):
    # Sliding window: only send the last 8 messages to save tokens
    recent_messages = messages[-8:] if len(messages) > 8 else messages
    history = []
    for m in recent_messages[:-1]:
        role = "user" if m["role"] == "user" else "model"
        history.append({"role": role, "parts": [m["content"]]})
    
    try:
        # Create a temporary model instance with the specific system instruction
        chat_model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system_prompt
        )
        chat = chat_model.start_chat(history=history)
        response = chat.send_message(recent_messages[-1]["content"])
        return response.text
    except exceptions.ResourceExhausted:
        return "⚠️ **Rate limit reached.** The free tier allows 15 requests per minute. Please wait 30 seconds and try again."
    except Exception as e:
        return f"⚠️ **Error:** {str(e)}"

# ── 6. SIDEBAR & LOGIC ───────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ EthicsBot")
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="⚡" if msg["role"] == "assistant" else "🎓"):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask about engineering ethics..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🎓"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Thinking…"):
            reply = get_gemini_response(st.session_state.messages, SYSTEM_PROMPTS[mode])
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
