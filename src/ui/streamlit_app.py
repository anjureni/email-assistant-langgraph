import streamlit as st
import urllib.parse
import json
import os

from src.workflow.langgraph_flow import generate_email_with_agents
from src.utils.pdf_export import build_email_pdf

st.set_page_config(page_title="AI-Powered Email Assistant", layout="wide", page_icon="📧")

PROFILE_PATH = os.path.join("src", "memory", "user_profiles.json")

def get_prompt_history(profile_key: str):
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        prof = data.get(profile_key) or data.get("formal") or next(iter(data.values()))
        return prof.get("prompt_history", [])
    except Exception:
        return []

def guardrails_prompt(prompt: str) -> bool:
    """Basic guardrails: block empty, offensive, or forbidden content."""
    forbidden_keywords = ["password",
    "ssn",
    "social security",
    "credit card",
    "bank account",
    "wire transfer",
    "phishing",
    "hack"]
    if not prompt.strip():
        return False
    lowered = prompt.lower()
    for word in forbidden_keywords:
        if word in lowered:
            return False
    return True

# ------------------ CSS ------------------
st.markdown(
    """
    <style>
      /* Page width + top spacing */
      div.block-container{
        padding-top: 0.8rem !important;
        padding-bottom: 0.8rem !important;
        max-width: 1200px;
      }

      /* Header */
      .app-header{
        text-align:center;
        margin: 0.3rem 0 0.6rem 0;
      }
      .app-header h1{
        margin:0;
        font-size: 44px;
        font-weight: 800;
        line-height: 1.1;
      }

      /* Output card */
      .card {
        background: #ffffff;
        border-radius: 14px;
        padding: 14px 16px;   /* ⬅ reduced padding */
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.06);
      }

      /* 🔽 Reduce spacing between elements inside right panel */
      .card h3, .card h2 {
        margin-bottom: 0.4rem !important;
      }

      /* Reduce spacing between Streamlit widgets */
      div[data-testid="stVerticalBlock"] > div {
        margin-bottom: 0.4rem !important;
      }

      /* Reduce label spacing */
      label {
        margin-bottom: 0.2rem !important;
      }

      /* Rounded inputs */
      div[data-testid="stTextInput"] input,
      div[data-testid="stTextArea"] textarea,
      div[data-testid="stSelectbox"] div{
        border-radius: 10px !important;
      }
    </style>
    """,
    unsafe_allow_html=True
)


# ------------------ Session state ------------------
st.session_state.setdefault("draft", "")
st.session_state.setdefault("subject", "")
st.session_state.setdefault("body", "")
st.session_state.setdefault("prompt_history_session", [])
st.session_state.setdefault("_last_tone", "formal")

# ------------------ LEFT SIDE BAR: controls + inputs + history ------------------
with st.sidebar:
    st.markdown("## Controls")

    selected_tone = st.selectbox("✍️ Tone", ["formal", "casual", "assertive"], key="tone")
    length = st.selectbox("📝 Message length", ["short", "medium", "long"], index=1)

    # Reset session history if tone changes
    if st.session_state["_last_tone"] != selected_tone:
        st.session_state["prompt_history_session"] = []
        st.session_state["_last_tone"] = selected_tone

    #st.divider()

    st.markdown("## Compose")

    with st.form("sidebar_compose_form", clear_on_submit=False):
      sender_name = st.text_input("Your name (sender)")
      recipient_name = st.text_input("Recipient Name (optional)")
      prompt = st.text_area("What do you want to write?", height=120)
      run_btn = st.form_submit_button("🚀 Generate Email", type="primary")



    #st.divider()

    # History section
    show_history = st.toggle("🕑 Show History", value=False)
    if show_history:
        st.subheader(f"Session Prompt History ({selected_tone})")
        session_history = st.session_state.get("prompt_history_session", [])
        if session_history:
            for i, h in enumerate(session_history[-10:], 1):
                st.markdown(f"**{i}.** {h}")
        else:
            st.info("No prompt history yet for this session.")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<small style='color:gray;'>Powered by LangGraph & OpenAI</small>", unsafe_allow_html=True)

# ------------------ MAIN (right side): header in middle + output ------------------
st.markdown(
    """
    <div class="app-header">
      <h1>📧 AI-Powered Email Assistant</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Run agents when button clicked
if run_btn:
    if not guardrails_prompt(prompt):
        st.error("⚠️ Sorry — I can’t generate this email because it may contain sensitive or restricted content. "
                   "Please remove sensitive details and try again.")
    else:
        st.session_state["prompt_history_session"].append(prompt)
        combined_prompt = "\n\n".join(st.session_state["prompt_history_session"])

        raw = {
            "prompt": combined_prompt,
            "tone": selected_tone,
            "sender_name": sender_name,
            "recipient_name": recipient_name,
            "length": length,
        }

        with st.spinner("Running agents (Intent → Tone → Draft → Review)…"):
            st.session_state["draft"] = generate_email_with_agents(raw)

        # --- Clear session prompt history if the output is a guardrail block message ---
        if st.session_state["draft"].startswith("⚠️ Sorry — I can’t generate this email"):
            st.session_state["prompt_history_session"] = []

# Parse draft into subject/body
draft_text = st.session_state["draft"]
subject = ""
body = ""

if draft_text and "Subject:" in draft_text:
    lines = draft_text.split("\n", 1)
    subject = lines[0].replace("Subject:", "").strip()
    body = lines[1].strip() if len(lines) > 1 else ""
else:
    body = draft_text

# ------------------ Output card ------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("### Email Output")


st.session_state["subject"] = st.text_input("Subject", value=subject)
st.session_state["body"] = st.text_area("Body", value=body, height=300)

if st.session_state["body"].strip():
    subject_encoded = urllib.parse.quote(st.session_state["subject"])
    body_encoded = urllib.parse.quote(st.session_state["body"])
    mailto_link = f"mailto:?subject={subject_encoded}&body={body_encoded}"

    st.markdown(f"📨 **Open in your mail app:** [Click to compose]({mailto_link})")

    pdf_bytes = build_email_pdf(st.session_state["subject"], st.session_state["body"])
    st.download_button(
        label="⬇️ Download as PDF",
        data=pdf_bytes,
        file_name="email_draft.pdf",
        mime="application/pdf"
    )

st.markdown("</div>", unsafe_allow_html=True)
