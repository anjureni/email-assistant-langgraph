from src.integrations.openai_client import generate_email

def review_email(draft: str, tone: str) -> str:
    prompt = f"""
You are a strict email reviewer.
Fix grammar, clarity, and ensure tone is {tone}.
Return ONLY the improved email with Subject + Body.

DRAFT:
{draft}
"""
    return generate_email(prompt, tone="formal")