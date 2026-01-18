# AI-Powered Email Assistant: Quick Reference

This project is an AI-powered Email Assistant built with Streamlit and LangGraph. It uses a multi-agent workflow to generate, review, and export emails with configurable tone and length.

## High-Level Architecture (ASCII)
```
+-------------------+         +-------------------+         +--------------------------+
|   User (Browser)  +-------> |   Streamlit App   +-------> | LangGraph Workflow Engine|
+-------------------+         +-------------------+         +--------------------------+
                                                                |
                                                                v
                                                    +--------------------------+
                                                    |      Agents Pipeline     |
                                                    +--------------------------+
                                                      |   |   |   |   |   |   |
                                                      v   v   v   v   v   v   v
                                                    [Input][Intent][Tone][Draft][Personalize][Review][Router]
                                                                |
                                                                v
                                                +-------------------------------+
                                                | User Profiles/History (JSON)   |
                                                +-------------------------------+
                                                                |
                                                                v
                                                +-------------------------------+
                                                |      PDF Export Utility        |
                                                +-------------------------------+
                                                                |
                                                                v
                                                +-------------------------------+
                                                |         OpenAI API             |
                                                +-------------------------------+
```

## Workflow Diagram (ASCII)
```
User Input
   |
   v
Input Parser Agent
   |
   v
Profile Loader
   |
   v
Intent Detector
   |
   v
Tone Stylist
   |
   v
Draft Writer
   |
   v
Personalization
   |
   v
Review & Validator
   |
   v
+---------Router---------+
|   (retry?)             |
|   Yes --> Draft Writer |
|   No  --> Finalize     |
+-----------------------+
   |
   v
Finalize & Save
   |
   v
Output (Subject/Body, Export)
```

## Guardrails (Input Validation)
- The app uses a guardrails function to block empty, offensive, or forbidden content in the prompt.
- Forbidden keywords include: `hack`, `scam`, `phish`, `offensive`, `hate`, `illegal`.
- If the prompt is empty or contains any forbidden word, email generation is blocked and an error is shown.
- This helps ensure safe and appropriate use of the assistant.

## Quick Start
1. Clone the repo and install dependencies:
   ```bash
   git clone <repo-url>
   cd email-assistant-langgraph
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Add your OpenAI API key to your environment:
   ```bash
   export OPENAI_API_KEY=your_key_here
   export MODEL_NAME=gpt-4o-mini
   ```
3. Run the Streamlit app:
   ```bash
   PYTHONPATH=. streamlit run src/ui/streamlit_app.py
   # or open http://localhost:8501/
   ```

## Usage
- Enter sender name, recipient name, tone, length, and your prompt.
- Click **Generate Email**.
- Edit the subject/body if needed.
- Export: open in email client or download as PDF.

---
For more details, see `architecture.md` or the main `README.md`.
