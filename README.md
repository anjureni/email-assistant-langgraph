# AI-Powered Email Assistant (LangGraph + Streamlit)

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
## High-Level Architecture
User → Streamlit UI → LangGraph Orchestrator → Agents → Final Email Output

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


Demo Steps
Enter Sender Name
Choose Tone and Length
Enter Prompt
Click Generate
Show Subject + Body fields
Click “Re-run Review only” and show improved grammar
Click “Re-draft” to generate a new version
Export to PDF / Open in email client

