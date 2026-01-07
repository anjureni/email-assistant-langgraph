from src.integrations.openai_client import generate_email as _llm_call

def detect_intent(prompt: str) -> str:
    system = (
        "Classify the intent of this email request. "
        "Return ONLY one label from: outreach, follow_up, apology, information, internal_update, other."
    )
    user = f"Request: {prompt}"
    label = _llm_call(user, tone="formal")  # reuse OpenAI call; we'll constrain output below

    label = label.strip().lower()
    allowed = {"outreach","follow_up","apology","information","internal_update","other"}
    for a in allowed:
        if a in label:
            return a
    return "other"