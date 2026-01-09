import streamlit as st
import urllib.parse

from src.workflow.langgraph_flow import generate_email_with_agents
from src.utils.pdf_export import build_email_pdf

st.set_page_config(page_title="AI-Powered Email Assistant", layout="wide")
st.title("📧 AI-Powered Email Assistant ")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input")
    tone = st.selectbox("Tone", ["formal", "casual", "assertive"])
    length = st.selectbox("Message length", ["short", "medium", "long"], index=1)
    sender_name = st.text_input("Your name (sender)")
    recipient_name = st.text_input("Recruiter / Recipient Name (optional)")
    company_name = st.text_input("Company Name (optional)")
    prompt = st.text_area("What do you want to write?", height=180)
    extra_context = st.text_area("Extra context (optional)", height=120)
    run_btn = st.button("Generate Email", type="primary")

with col2:
    st.subheader("Output")

    if "draft" not in st.session_state:
        st.session_state["draft"] = ""

    if run_btn:
        if not prompt.strip():
            st.error("Please enter your request.")
        else:
            raw = {
                "prompt": prompt,
                "tone": tone,
                "sender_name": sender_name,
                "recipient_name": recipient_name,
                "company_name": company_name,
                "extra_context": extra_context,
                "length": length,
            }
            with st.spinner("Running agents (Intent → Tone → Draft → Review)…"):
                st.session_state["draft"] = generate_email_with_agents(raw)

    # ---- Subject & Body split ----
    draft_text = st.session_state["draft"]

    subject = ""
    body = ""

    if draft_text and "Subject:" in draft_text:
        lines = draft_text.split("\n", 1)
        subject = lines[0].replace("Subject:", "").strip()
        body = lines[1].strip() if len(lines) > 1 else ""
    else:
        body = draft_text

    subject = st.text_input("Subject", value=subject)
    body = st.text_area("Body", value=body, height=420)

    # Store back to session state
    st.session_state["subject"] = subject
    st.session_state["body"] = body

    # ---- Export Options ----
    if st.session_state.get("body"):
        subject_encoded = urllib.parse.quote(st.session_state.get("subject", ""))
        body_encoded = urllib.parse.quote(st.session_state.get("body", ""))

        mailto_link = f"mailto:?subject={subject_encoded}&body={body_encoded}"
        st.markdown(f"📨 **Open Email Draft in Your Mail App:** [Click here to compose email]({mailto_link})")

        pdf_bytes = build_email_pdf(
            st.session_state.get("subject", ""),
            st.session_state.get("body", "")
        )

        st.download_button(
            label="⬇️ Download as PDF",
            data=pdf_bytes,
            file_name="email_draft.pdf",
            mime="application/pdf"
        )
