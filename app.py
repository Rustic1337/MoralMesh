import streamlit as st
import anthropic

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
col1, col2 = st.columns([3, 1])
with col1:
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

🇺🇸 NORTH AMERICA:
- Therac-25 (1985-1987): Radiation therapy software bug killed 6 patients — software ethics, testing
- Challenger Space Shuttle (1986): O-ring failure in cold weather, pressure to launch — whistleblowing, management override
- Columbia Space Shuttle (2003): Foam strike ignored — organizational culture, safety culture
- Northeast Blackout (2003): Cascading power grid failure — system safety, negligence
- Deepwater Horizon (2010): BP oil spill — cost-cutting, safety shortcuts, environmental ethics
- Boeing 737 MAX (2018-2019): MCAS software flaw killed 346 — software safety, profit over safety, whistleblowing ignored
- OceanGate Titan Submersible (2023): Implosion killed 5 — ignored safety warnings, rejected certification, whistleblower fired

🇩🇪 EUROPE:
- Volkswagen Emissions Scandal (2015): Defeat device software cheated emissions tests — deliberate deception, corporate ethics
- Hyatt Regency Walkway Collapse (1981, USA/global study): Design change without engineer approval

🌏 ASIA/SOUTH ASIA:
- Bhopal Gas Tragedy (1984, India): Union Carbide chemical leak killed thousands — corporate negligence, right to know, global ethics
- Fukushima Nuclear Disaster (2011, Japan): Tsunami overwhelmed plant — risk assessment, regulatory capture
- Rana Plaza Collapse (2013, Bangladesh): Garment factory building collapse, 1,134 killed — building codes, ethical supply chains
- Samsung Galaxy Note 7 Battery Fire (2016, South Korea): Rushed design, battery explosions — product safety testing

🇵🇰 PAKISTAN CASE STUDIES:
- Baldia Town Factory Fire (2012, Karachi): 259+ workers killed at Ali Enterprises garment factory — locked exits, no fire alarms, no sprinklers, illegal construction, failed inspections. PEC and building codes ignored. Ethical lessons: public safety obligation, regulatory enforcement, whistleblowing
- Attabad Landslide & Dam (2010, Hunza): 55 million cubic meters of rock blocked Hunza River, 20 killed, 25,000 displaced, 22km of Karakoram Highway submerged. Engineers had to manage natural dam emergency — risk assessment, emergency engineering ethics, infrastructure in disaster-prone regions
- Gul Plaza Fire (2026, Karachi): Major shopping centre fire, 23+ killed — 70% of Karachi buildings still lack fire safety systems, structural collapse during rescue
- Pakistan construction industry ethics: PEC code rarely followed, bribery in project approvals, substandard materials (less steel in concrete), absent engineers signing off on work they didn't supervise
- CPEC (China-Pakistan Economic Corridor) infrastructure projects: questions about local vs. international engineering standards, labor safety, environmental impact assessments
- Tarbela and Mangla Dams: historical engineering achievements but questions about displacement of communities and long-term silting ethics

FORMATTING:
- Bold key terms with **term**
- Use numbered lists for multi-point answers
- Cite IEEE canons or NSPE sections when applicable
- Keep responses 3-6 paragraphs unless more detail is needed
- Be academic and professional in tone""",

    "🧠 Quiz Me": """You are EthicsBot in QUIZ MODE for an EE ethics course.
Ask ONE multiple-choice question (A/B/C/D) at a time. Cover:
- IEEE Code of Ethics canons, NSPE Code
- Global case studies: Therac-25, Challenger, Boeing 737 MAX, OceanGate Titan, VW Emissions, Bhopal, Fukushima
- Pakistan case studies: Baldia Factory Fire, Attabad landslide, PEC code
- Whistleblowing, conflicts of interest, ethical frameworks
After the student answers: say correct ✅ or incorrect ❌, explain the ethical lesson, then offer another question.
Vary difficulty and topics. Make questions relevant to EE students.""",

    "📖 Ethical Scenario": """You are EthicsBot in ETHICAL SCENARIO MODE for an EE ethics course.
Present realistic engineering dilemmas — mix global and Pakistan-specific scenarios such as:
- An engineer in Pakistan discovers substandard wiring in a high-rise but the contractor is politically connected
- A software engineer discovers a bug in medical device firmware before launch — management wants to ship anyway
- An EE working on CPEC infrastructure is pressured to approve designs without proper review
- A factory engineer knows exit doors are locked but fears losing their job
Ask what the student would do. Analyze using IEEE canons, PEC code, and ethical frameworks.
Make it feel like a real professional situation a Pakistani EE graduate might face.""",

    "📝 Exam Prep": """You are EthicsBot in EXAM PREP MODE for an EE ethics course.
Give concise exam-ready answers. Highlight key definitions and memorable facts.
Provide practice questions with model answers when asked.
Focus on: IEEE canons, NSPE/PEC codes, case studies (including Pakistan ones), ethical frameworks.
When covering Pakistan cases: Baldia Factory Fire, Attabad landslide, construction ethics, PEC code enforcement.
Give tips on structuring ethics exam answers. Be efficient — students need clear, memorable answers."""
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
        "PEC Code (Pakistan)": "What is the Pakistan Engineering Council (PEC) Code of Ethics and how does it apply to EE graduates?",
        "Utilitarianism": "Explain utilitarian ethics with engineering examples",
        "Deontological Ethics": "Explain deontological ethics and Kantian duty in engineering",
        "Virtue Ethics": "What is virtue ethics and how does it apply to professional engineers?",
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
        "🇺🇸 Boeing 737 MAX": "Explain the Boeing 737 MAX crashes and the engineering ethics failures — MCAS, whistleblowing, profit over safety",
        "🇺🇸 OceanGate Titan": "Tell me about the OceanGate Titan submersible implosion in 2023 and its engineering ethics lessons",
        "🇩🇪 VW Emissions Scandal": "What was the Volkswagen emissions scandal and what are the engineering ethics lessons?",
        "🇮🇳 Bhopal Gas Tragedy": "Explain the Bhopal gas tragedy from an engineering ethics perspective",
        "🇯🇵 Fukushima Nuclear": "What were the engineering ethics failures in the Fukushima nuclear disaster?",
        "🇧🇩 Rana Plaza Collapse": "Tell me about the Rana Plaza garment factory collapse in Bangladesh and its engineering ethics lessons",
    }
    for label, q in global_cases.items():
        if st.button(label, use_container_width=True, key=f"global_{label}"):
            st.session_state.pending_question = q

    st.markdown("---")
    st.markdown("**🇵🇰 Pakistan Case Studies**")
    pk_cases = {
        "Baldia Factory Fire (2012)": "Explain the Baldia Town factory fire in Karachi 2012 in detail — what happened, what engineering ethics were violated, what should engineers have done, and what lessons does it teach?",
        "Attabad Landslide (2010)": "Tell me about the Attabad landslide in Hunza 2010 — what happened, the engineering challenges, ethics of emergency response, and lessons for engineers in Pakistan",
        "Gul Plaza Fire (2026)": "Tell me about the Gul Plaza fire in Karachi 2026 and what it reveals about Pakistan's ongoing building safety crisis",
        "Construction Ethics in Pakistan": "What are the major engineering ethics issues in Pakistan's construction industry? Discuss PEC code violations, bribery, substandard materials, and how engineers should respond",
        "CPEC Engineering Ethics": "What are the engineering ethics questions raised by CPEC (China-Pakistan Economic Corridor) infrastructure projects?",
        "PEC & Regulatory Challenges": "What is the Pakistan Engineering Council and why is its code of ethics rarely followed in practice? What should change?",
    }
    for label, q in pk_cases.items():
        if st.button(label, use_container_width=True, key=f"pk_{label}"):
            st.session_state.pending_question = q

    st.markdown("---")
    st.markdown("**⚖️ Key Topics**")
    topics = {
        "Whistleblowing": "When is an engineer ethically required to blow the whistle? How should they do it safely?",
        "Conflicts of Interest": "What are conflicts of interest in engineering? Give examples",
        "Public Safety Obligation": "What are an electrical engineer's obligations to public safety under IEEE and NSPE?",
        "Informed Consent": "Explain informed consent in engineering contexts with examples",
        "Bribery & Corruption": "How should engineers handle pressure to engage in bribery or corruption?",
    }
    for label, q in topics.items():
        if st.button(label, use_container_width=True, key=f"topic_{label}"):
            st.session_state.pending_question = q

    st.markdown("---")
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

# ── Handle sidebar question injection ───────────────────────
if st.session_state.pending_question:
    q = st.session_state.pending_question
    st.session_state.pending_question = None
    st.session_state.messages.append({"role": "user", "content": q})

# ── Display messages ─────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="⚡" if msg["role"] == "assistant" else "🎓"):
        st.markdown(msg["content"])

# ── Welcome ──────────────────────────────────────────────────
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="⚡"):
        st.markdown("""**Welcome to EthicsBot!** Your AI assistant for Electrical Engineering Ethics.

I now cover **global + Pakistan-specific** engineering ethics content:

🌍 **Global Cases** — Boeing 737 MAX, OceanGate Titan, Therac-25, Challenger, Bhopal, Fukushima, VW Emissions, Rana Plaza & more

🇵🇰 **Pakistan Cases** — Baldia Town Factory Fire (2012), Attabad Landslide (2010), Gul Plaza Fire (2026), CPEC ethics, PEC Code, construction industry corruption

⚖️ **Codes** — IEEE Code of Ethics, NSPE Code, Pakistan Engineering Council (PEC) Code

📚 **Modes** — Switch between Q&A, Quiz, Ethical Scenario (Pakistan-context), and Exam Prep using the dropdown above.

Use the **sidebar** to explore any topic or case study, or just type your question below!""")

# ── Auto-trigger if sidebar was clicked ──────────────────────
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_msg = st.session_state.messages[-1]["content"]
    # Check if we need to generate a response for this message
    needs_response = len(st.session_state.messages) == 0 or st.session_state.messages[-1]["role"] == "user"

    if needs_response:
        with st.chat_message("assistant", avatar="⚡"):
            client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            with st.spinner("Thinking…"):
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1200,
                    system=SYSTEM_PROMPTS[mode],
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                )
            reply = response.content[0].text
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

# ── Chat input ───────────────────────────────────────────────
if prompt := st.chat_input("Ask about engineering ethics, IEEE codes, Pakistan cases, exam prep…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🎓"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="⚡"):
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        with st.spinner("Thinking…"):
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1200,
                system=SYSTEM_PROMPTS[mode],
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
        reply = response.content[0].text
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
