import os
from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, APITimeoutError

load_dotenv()

# Create client ONCE with retries + timeout
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=60.0,     # seconds
    max_retries=3     # retry on transient failures
)

def generate_email(prompt: str, tone: str = "formal") -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "ERROR: OPENAI_API_KEY is missing. Add it to your .env file."

    model = os.getenv("MODEL_NAME", "gpt-4o-mini")

    system = (
        "You are an expert email assistant. "
        f"Write a complete email with a subject line. Tone: {tone}."
    )
    user = f"Write an email based on this request:\n{prompt}"

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.5,
        )
        return resp.choices[0].message.content.strip()

    except (APIConnectionError, APITimeoutError):
        # Fallback so app & demo never crash
        return (
            "Subject: Temporary Connection Issue\n\n"
            "Hi,\n\n"
            "The AI service is temporarily unavailable due to a network issue. "
            "This is a fallback response to ensure the workflow continues.\n\n"
            "Please try again in a moment.\n\n"
            "Best regards,\n"
            "Email Assistant"
        )
