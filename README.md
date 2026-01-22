# AI-Powered Email Assistant (LangGraph + Streamlit) By Anju Susan Raju

## Overview
This project is an AI-powered Email Assistant built using **LangGraph** and **Streamlit**.  
It uses a **multi-agent architecture** to generate emails with configurable **tone** and **length**, and a review agent to improve grammar and clarity.
## Key Features
- Multi-agent workflow using LangGraph
- Tone selection: Formal / Casual / Assertive
- Length control: Short / Medium / Long
- Subject + Body separation for easy editing
- Review-only rerun (grammar/tone validation)
- Re-draft option (regenerate a fresh email)
- Export: open in email client + download PDF
- Public-safe: sender name is entered by user (not hardcoded)

## Guardrails (Input Validation)
- The app uses a guardrails function to block empty, offensive, or forbidden content in the prompt.
- Forbidden keywords include:  "password","ssn","social security", "credit card",
    "bank account","wire transfer","phishing", "hack"

- If the prompt is empty or contains any forbidden word, email generation is blocked and an error is shown.
- This helps ensure safe and appropriate use of the assistant.
## High-Level Architecture
User → Streamlit UI → LangGraph Orchestrator → Agents → Final Email Output
<img width="582" height="387" alt="image" src="https://github.com/user-attachments/assets/ef08ab98-9b19-4991-a1d0-a7c58d711905" />

# Agentic Orchestration Overview

<img width="657" height="292" alt="image" src="https://github.com/user-attachments/assets/e0ad216c-581e-4f3f-a771-0602ebb70de1" />

## Work FLOW Diagaram
<img width="547" height="88" alt="image" src="https://github.com/user-attachments/assets/5a87b572-93bd-4182-aba9-7aceae4e465c" />


Agents:
1. Input Parser (validates and structures user input)
2. Intent Detection (detects email purpose)
3. Tone Stylist (creates tone rules)
4. Draft Writer (generates email draft + subject)
5. Personalization (adds sender name + signoff from memory)
6. Review & Validator (fixes grammar, tone alignment, coherence)
## How to Run (Local)
### 1) Clone repo
```bash
git clone <repo-url>
cd email-assistant-langgraph


2) Create and activate virtual environment (Mac)
python -m venv .venv
source .venv/bin/activate
3) Install dependencies
pip install -r requirements.txt
4) Add OpenAI key
OPENAI_API_KEY=your_key_here
MODEL_NAME=gpt-4o-mini
5) Run Streamlit app
PYTHONPATH=. streamlit run src/ui/streamlit_app.py
or open:-
http://localhost:8501/
