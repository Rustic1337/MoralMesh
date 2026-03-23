import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="EthicsBot – EE Ethics", page_icon="⚡", layout="wide")

# 2. STYLING
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f5f4f0; }
.block-container { padding-top: 1.5rem; }
[data-testid="stChatMessage"] { background: white; border-radius: 12px; border: 1px solid #e2ddd4; margin-bottom: 6px; }
section[data-testid="stSidebar"] { background: #0f1f3d !important; }
section[data-testid="stSidebar"] * { color: rgba(255,255,255,0.85) !important; }
section[data-testid="stSidebar"] .stButton button {
    background: transparent !important; border: 1px solid rgba(255,255,255,0.15) !important;
    color: rgba(255,255,255,0.8) !important; border-radius: 8px !important;
    text-align: left !important; font-size: 0.78rem !important; padding: 6px 10px !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(201,168,76,0.2) !important; border-color: #c9a84c !important; color: #f0d98a !important;
}
</style>
""", unsafe_allow_html=True)

# 3. GLOBAL API INITIALIZATION
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
except Exception as e:
    st.error("API Configuration failed. Please check your Streamlit Secrets.")

# 4. HEADER & MODE SELECTOR
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
    "💬 General Q&A": """You are EthicsBot, a specialized assistant for engineering ethics. 
    Expertise: IEEE, NSPE, and PEC Codes. 
    CASE STUDIES: Therac-25, Challenger, Columbia, Boeing 737 MAX, OceanGate, Baldia Town, Attabad Landslide, Gul Plaza Fire.
    Cite codes where applicable. Be academic and professional.""",
    "🧠 Quiz Me": "You are EthicsBot in QUIZ MODE. Ask ONE multiple-choice question at a time.",
    "📖 Ethical Scenario": "Present realistic engineering dilemmas like the Baldia Town Fire and ask for the student's reaction.",
    "📝 Exam Prep": "Give concise exam-ready answers regarding whistleblowing, conflict of interest, and professional ethics."
}

# 5. SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_mode" not in st.session_state:
    st.session_state.current_mode = mode
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

if st.session_state.current_mode != mode:
    st.session_state.messages = []
    st.session_state.current_mode = mode

# 6. IMPROVED API HELPER
def get_gemini_response(messages, system_prompt):
    recent_messages = messages[-10:] if len(messages) > 10 else messages
    history = []
    for m in recent_messages[:-1]:
        role = "user" if m["role"] == "user" else "model"
        history.append({"role": role, "parts": [m["content"]]})
    
    try:
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

# 7. SIDEBAR & LOGIC
with st.sidebar:
    st.markdown("### ⚡ EthicsBot")
    st.markdown("---")
    if st.button("Whistleblowing", use_container_width=True):
        st.session_state.pending_question = "When is an engineer ethically required to blow the whistle?"
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if st.session_state.pending_question:
    q = st.session_state.pending_question
    st.session_state.pending_question = None
    st.session_state.messages.append({"role": "user", "content": q})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="⚡" if msg["role"] == "assistant" else "🎓"):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about engineering ethics..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🎓"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Thinking…"):
            reply = get_gemini_response(st.session_state.messages, SYSTEM_PROMPTS[mode])
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
