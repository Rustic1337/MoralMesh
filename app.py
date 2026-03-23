import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="EthicsBot – EE Ethics", page_icon="⚡", layout="wide")

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

# ── Header ──────────────────────────────────────────────────
st.markdown("""
<div style="background:#0f1f3d;padding:16px 24px;border-radius:12px;border-bottom:3px solid #c9a84c;margin-bottom:20px">
  <h2 style="color:white;margin:0;font-size:1.25rem">⚡ EthicsBot — Electrical Engineering Ethics</h2>
  <p style="color:#f0d98a;margin:4px 0 0;font-size:0.72rem;letter-spacing:0.08em;text-transform:uppercase">
    IEEE · NSPE · Global &amp; Pakistan Case Studies · Professional Ethics · Exam Prep
  </p>
</div>
""", unsafe_allow_html=True)

# ── Mode selector ────────────────────────────────────────────
mode = st.selectbox("Mode", [
    "💬 General Q&A",
    "🧠 Quiz Me",
    "📖 Ethical Scenario",
    "📝 Exam Prep"
], label_visibility="collapsed")

SYSTEM_PROMPTS = {
    "💬 General Q&A": """You are EthicsBot, a specialized assistant for engineering ethics in an Electrical Engineering university course.

Your expertise covers:

CODES & FRAMEWORKS:
- IEEE Code of Ethics (10 fundamental canons) and NSPE Code of Ethics
- Pakistan Engineering Council (PEC) Code of Ethics
- Ethical frameworks: utilitarianism, deontological ethics, virtue ethics applied to engineering

KEY TOPICS:
- Public safety obligations, whistleblowing (when required, how to do it, protections)
- Conflicts of interest, bribery, corruption, informed consent
- Professional responsibility, intellectual property, confidentiality
- Engineering in developing countries, regulatory challenges

GLOBAL CASE STUDIES (know these in detail):

NORTH AMERICA:
- Therac-25 (1985-1987): Radiation therapy software bug killed 6 patients
- Challenger Space Shuttle (1986): O-ring failure, pressure to launch, whistleblowing ignored
- Columbia Space Shuttle (2003): Foam strike ignored, organizational culture failure
- Northeast Blackout (2003): Cascading power grid failure, negligence
- Deepwater Horizon (2010): BP oil spill, cost-cutting, safety shortcuts
- Boeing 737 MAX (2018-2019): MCAS software flaw killed 346, profit over safety
- OceanGate Titan Submersible (2023): Implosion killed 5, ignored safety warnings, whistleblower fired

EUROPE:
- Volkswagen Emissions Scandal (2015): Defeat device software cheated emissions tests

ASIA/SOUTH ASIA:
- Bhopal Gas Tragedy (1984, India): Union Carbide chemical leak killed thousands
- Fukushima Nuclear Disaster (2011, Japan): Tsunami overwhelmed plant, regulatory capture
- Rana Plaza Collapse (2013, Bangladesh): 1,134 killed, building codes ignored
- Samsung Galaxy Note 7 Battery Fire (2016): Rushed design, battery explosions

PAKISTAN CASE STUDIES:
- Baldia Town Factory Fire (2012, Karachi): 259+ workers killed, locked exits, no fire alarms, failed inspections
- Attabad Landslide & Dam (2010, Hunza): 55 million cubic meters of rock blocked Hunza River, 25,000 displaced
- Gul Plaza Fire (2026, Karachi): 23+ killed, 70% of Karachi buildings lack fire safety
- Pakistan construction ethics: PEC code violations, bribery, substandard materials
- CPEC infrastructure ethics: standards, labor safety, environmental impact

FORMATTING:
- Bold key terms
- Use numbered lists for multi-point answers
- Cite IEEE canons or NSPE sections when applicable
- Keep responses 3-6 paragraphs
- Be academic and professional""",

    "🧠 Quiz Me": """You are EthicsBot in QUIZ MODE for an EE ethics course.
Ask ONE multiple-choice question (A/B/C/D) at a time. Cover IEEE Code, NSPE Code, global and Pakistan case studies, whistleblowing, ethical frameworks.
After the student answers: say correct or incorrect, explain the ethical lesson, then offer another question.""",

    "📖 Ethical Scenario": """You are EthicsBot in ETHICAL SCENARIO MODE for an EE ethics course.
Present realistic engineering dilemmas including Pakistan-specific scenarios such as:
- An engineer in Pakistan discovers substandard wiring in a high-rise but contractor is politically connected
- A software engineer finds a bug in medical device firmware before launch, management wants to ship anyway
- An EE on CPEC infrastructure is pressured to approve designs without proper review
Ask what the student would do. Analyze using IEEE canons, PEC code, and ethical frameworks.""",

    "📝 Exam Prep": """You are EthicsBot in EXAM PREP MODE for an EE ethics course.
Give concise exam-ready answers. Highlight key definitions and memorable facts.
Provide practice questions with model answers when asked.
Focus on IEEE canons, NSPE/PEC codes, case studies including Pakistan ones, ethical frameworks."""
}

# ── Session state ────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_mode" not in st.session_state:
    st.session_state.current_mode = mode
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

if st.session_state.current_mode != mode:
    st.session_state.messages = []
    st.session_state.current_mode = mode

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ EthicsBot")
    st.markdown("---")

    st.markdown("**📋 Codes & Frameworks**")
    codes = {
        "IEEE Code of Ethics": "Explain the IEEE Code of Ethics and all 10 fundamental canons in detail",
        "NSPE Code": "What is the NSPE Code of Ethics? Explain its key principles",
        "PEC Code (Pakistan)": "What is the Pakistan Engineering Council (PEC) Code of Ethics?",
        "Utilitarianism": "Explain utilitarian ethics with engineering examples",
        "Deontological Ethics": "Explain deontological ethics and duty in engineering",
        "Virtue Ethics": "What is virtue ethics and how does it apply to engineers?",
    }
    for label, q in codes.items():
        if st.button(label, use_container_width=True, key=f"code_{label}"):
            st.session_state.pending_question = q

    st.markdown("---")
    st.markdown("**🌍 Global Case Studies**")
    global_cases = {
        "🇺🇸 Therac-25": "Tell me about the Therac-25 radiation machine disaster and its ethics lessons",
        "🇺🇸 Challenger (1986)": "Explain the Challenger Space Shuttle disaster from an engineering ethics perspective",
        "🇺🇸 Columbia (2003)": "What were the engineering ethics failures in the Columbia Space Shuttle disaster?",
        "🇺🇸 Northeast Blackout": "What happened in the Northeast Blackout of 2003 and what were the engineering ethics failures?",
        "🇺🇸 Deepwater Horizon": "Explain the BP Deepwater Horizon oil spill and its engineering ethics lessons",
        "🇺🇸 Boeing 737 MAX": "Explain the Boeing 737 MAX crashes and the engineering ethics failures",
        "🇺🇸 OceanGate Titan": "Tell me about the OceanGate Titan submersible implosion 2023 and its engineering ethics lessons",
        "🇩🇪 VW Emissions": "What was the Volkswagen emissions scandal and the engineering ethics lessons?",
        "🇮🇳 Bhopal Gas Tragedy": "Explain the Bhopal gas tragedy from an engineering ethics perspective",
        "🇯🇵 Fukushima Nuclear": "What were the engineering ethics failures in the Fukushima nuclear disaster?",
        "🇧🇩 Rana Plaza": "Tell me about the Rana Plaza collapse in Bangladesh and its engineering ethics lessons",
    }
    for label, q in global_cases.items():
        if st.button(label, use_container_width=True, key=f"global_{label}"):
            st.session_state.pending_question = q

    st.markdown("---")
    st.markdown("**🇵🇰 Pakistan Case Studies**")
    pk_cases = {
        "Baldia Factory Fire (2012)": "Explain the Baldia Town factory fire in Karachi 2012 in detail — what happened, ethics violated, and lessons",
        "Attabad Landslide (2010)": "Tell me about the Attabad landslide in Hunza 2010 — engineering challenges and ethics",
        "Gul Plaza Fire (2026)": "Tell me about the Gul Plaza fire in Karachi 2026 and Pakistan's building safety crisis",
        "Construction Ethics PK": "What are the major engineering ethics issues in Pakistan's construction industry?",
        "CPEC Engineering Ethics": "What are the engineering ethics questions raised by CPEC projects?",
        "PEC & Regulatory Issues": "Why is the PEC code of ethics rarely followed in practice in Pakistan?",
    }
    for label, q in pk_cases.items():
        if st.button(label, use_container_width=True, key=f"pk_{label}"):
            st.session_state.pending_question = q

    st.markdown("---")
    st.markdown("**⚖️ Key Topics**")
    topics = {
        "Whistleblowing": "When is an engineer ethically required to blow the whistle?",
        "Conflicts of Interest": "What are conflicts of interest in engineering?",
        "Public Safety": "What are an electrical engineer's obligations to public safety?",
        "Informed Consent": "Explain informed consent in engineering contexts",
        "Bribery & Corruption": "How should engineers handle pressure to engage in bribery?",
    }
    for label, q in topics.items():
        if st.button(label, use_container_width=True, key=f"topic_{label}"):
            st.session_state.pending_question = q

    st.markdown("---")
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

# ── Handle sidebar click ─────────────────────────────────────
if st.session_state.pending_question:
    q = st.session_state.pending_question
    st.session_state.pending_question = None
    st.session_state.messages.append({"role": "user", "content": q})

# ── Gemini response helper ───────────────────────────────────
def get_gemini_response(messages, system_prompt):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt
    )
    # Build history for Gemini (all but last message)
    history = []
    for m in messages[:-1]:
        role = "user" if m["role"] == "user" else "model"
        history.append({"role": role, "parts": [m["content"]]})
    
    chat = model.start_chat(history=history)
    response = chat.send_message(messages[-1]["content"])
    return response.text

# ── Display messages ─────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="⚡" if msg["role"] == "assistant" else "🎓"):
        st.markdown(msg["content"])

# ── Welcome ──────────────────────────────────────────────────
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="⚡"):
        st.markdown("""**Welcome to EthicsBot!** Your AI assistant for Electrical Engineering Ethics.

I cover **global + Pakistan-specific** engineering ethics:

🌍 **Global Cases** — Boeing 737 MAX, OceanGate Titan, Therac-25, Challenger, Bhopal, Fukushima, VW Emissions, Rana Plaza & more

🇵🇰 **Pakistan Cases** — Baldia Town Factory Fire, Attabad Landslide, Gul Plaza Fire, CPEC ethics, PEC Code

⚖️ **Codes** — IEEE Code of Ethics, NSPE Code, Pakistan Engineering Council (PEC) Code

Use the **sidebar** to explore topics or just type your question below!""")

# ── Auto respond if sidebar was clicked ──────────────────────
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Thinking…"):
            reply = get_gemini_response(st.session_state.messages, SYSTEM_PROMPTS[mode])
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

# ── Chat input ───────────────────────────────────────────────
if prompt := st.chat_input("Ask about engineering ethics, IEEE codes, Pakistan cases, exam prep…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🎓"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("Thinking…"):
            reply = get_gemini_response(st.session_state.messages, SYSTEM_PROMPTS[mode])
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
