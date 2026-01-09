from src.integrations.openai_client import generate_email

def review_email(draft: str, tone: str) -> str:
    prompt = f"""
You are a Review & Validator Agent for email writing.

Your responsibilities:
1. Fix grammar, spelling, and punctuation.
2. Ensure the email tone is strictly '{tone}'.
3. Ensure contextual coherence:
   - The email has a clear purpose.
   - No missing greetings or sign-offs.
   - No contradictory or confusing sentences.
4. DO NOT add new information.
5. DO NOT change the original intent.
6. DO NOT remove important details.

Return ONLY the improved email.
Include Subject line and Body.

EMAIL TO REVIEW:
{draft}
"""
    # Use low creativity since this is validation, not generation
    return generate_email(prompt, tone=tone)
