# AI-Powered Email Assistant Architecture

## High-Level Architecture
This system is an AI Email Composer built with Streamlit and LangGraph. It uses multiple specialized agents to generate an email with tone and length controls, then reviews grammar and tone before showing the final draft. The final draft is editable (subject and body) and can be exported to an email client or downloaded as a PDF.

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

**Explanation:**
- The user interacts with the Streamlit UI.
- The UI calls the LangGraph workflow engine, which orchestrates the email generation process.
- The workflow engine coordinates a pipeline of agents (input parser, intent detector, tone stylist, draft writer, personalization, review, router).
- The system uses a memory layer (JSON) for user profiles and history, and integrates with OpenAI for LLM tasks and a PDF export utility for downloads.

---

## Workflow Diagram
This diagram shows the step-by-step flow of how an email is generated and refined.

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

**Explanation:**
- The user provides input (tone, length, prompt, sender/recipient).
- The input is parsed and normalized.
- The profile loader fetches user/tone preferences.
- The intent detector determines the purpose of the email.
- The tone stylist applies tone rules.
- The draft writer generates the initial draft.
- Personalization adds user-specific details.
- The review agent checks grammar, tone, and clarity.
- The router decides if a retry is needed (loops back to draft writer) or finalizes the draft.
- The finalized output is shown in the UI and can be exported.
