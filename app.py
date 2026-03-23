import streamlit as st
import google.generativeai as genai
from google.api_core import exceptions

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="EthicsBot – EE Ethics", page_icon="⚡", layout="wide") [cite: 1]

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
</style>
""", unsafe_allow_html=True) [cite: 1]

# 3. GLOBAL API INITIALIZATION (Moved outside the function for efficiency)
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
""", unsafe_allow_html=True) [cite: 1]

mode = st.selectbox("Mode", ["💬 General Q&A", "🧠 Quiz Me", "📖 Ethical Scenario", "📝 Exam Prep"], label_visibility="collapsed") [cite: 1]

# (SYSTEM_PROMPTS dictionary remains the same as your original file)
SYSTEM_PROMPTS = {
    "💬 General Q&A": "You are EthicsBot, specialized in IEEE, NSPE, and PEC codes... ",
    "🧠 Quiz Me": "You are EthicsBot in QUIZ MODE... ",
    "📖 Ethical Scenario": "Present realistic engineering dilemmas like the Baldia Town Fire... ",
    "📝 Exam Prep": "Give concise exam-ready answers regarding whistleblowing and ethics... "
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
    # Keep only the last 10 messages to avoid hitting Token limits
    recent_messages = messages[-10:] if len(messages) > 10 else messages
    
    history = []
    for m in recent_messages[:-1]:
        role = "user" if m["role"] == "user" else "model"
        history.append({"role": role, "parts": [m["content"]]})
    
    try:
        # Pass the system prompt directly into the model for each session
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

# 7. SIDEBAR & CHAT LOGIC (Same structure as original, calling improved helper)
# ... [rest of your sidebar and input logic]
