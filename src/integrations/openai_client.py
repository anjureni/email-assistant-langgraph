import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def generate_email(prompt: str, tone: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "ERROR: OPENAI_API_KEY is missing. Add it to your .env file."

    model = os.getenv("MODEL_NAME", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)

    system = (
        "You are an expert email assistant. "
        f"Write a complete email with a subject line. Tone: {tone}."
    )
    user = f"Write an email based on this request:\n{prompt}"

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.5,
    )
    return resp.choices[0].message.content.strip()