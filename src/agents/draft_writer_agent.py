from src.integrations.openai_client import generate_email

def write_draft(intent: str, tone_rules: str, prompt: str, recipient_name: str | None, company_name: str | None, extra_context: str | None) -> str:
    full_prompt = f"""
INTENT: {intent}
{tone_rules}

RECIPIENT_NAME: {recipient_name or "Recruiter"}
COMPANY_NAME: {company_name or "Company"}

USER REQUEST:
{prompt}

EXTRA CONTEXT:
{extra_context or ""}

Write:
- Subject line starting with "Subject:"
- Email body with greeting + paragraphs + sign-off placeholder [SIGNOFF] and signature placeholder [SIGNATURE]
"""
    return generate_email(full_prompt, tone="formal")