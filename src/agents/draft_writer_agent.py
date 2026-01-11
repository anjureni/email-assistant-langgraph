from src.integrations.openai_client import generate_email

def write_draft(
    intent: str,
    tone: str,                 # ✅ NEW
    tone_rules: str,
    prompt: str,
    recipient_name: str | None,
    company_name: str | None,
    extra_context: str | None,
    length: str,
) -> str:
    length_rules = {
        "short": "Keep it short: 4-6 sentences total.",
        "medium": "Keep it medium length: 6-8 sentences total.",
        "long": "Keep it detailed but not rambling: 10-14 sentences total."
    }.get(length, "Keep it medium length: 6-8 sentences total.")

    subject_rule = "You MUST include a subject line in the exact format 'Subject: ...' on the first line."

    full_prompt = f"""
You are an expert email assistant.

INTENT: {intent}
{tone_rules}
LENGTH RULE: {length_rules}
`   
SUBJECT RULE: {subject_rule}

RECIPIENT_NAME: {recipient_name or "Recipient"}
COMPANY_NAME: {company_name or "Company"}

USER REQUEST:
{prompt}

EXTRA CONTEXT:
{extra_context or ""}

Write the email with:
- First line must be: Subject: ...
- Greeting
- Clear body
- Ending
- Sign-off placeholder [SIGNOFF]
- Signature placeholder [SIGNATURE]

Return ONLY the email text.
"""
    return generate_email(full_prompt, tone=tone)   # ✅ pass label
