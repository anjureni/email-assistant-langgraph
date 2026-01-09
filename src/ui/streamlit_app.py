import streamlit as st
from src.workflow.langgraph_flow import generate_email_with_agents

st.set_page_config(page_title="AI Email Assistant", layout="wide")
st.title("📧 AI Email Assistant ")

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

    st.text_area("Editable Email", value=st.session_state["draft"], height=520)
