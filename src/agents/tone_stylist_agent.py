def tone_instructions(tone: str) -> str:
    tone = (tone or "formal").lower().strip()

    if tone == "casual":
        return "Tone: friendly, casual, simple. Keep it short. No overly formal phrases."
    if tone == "assertive":
        return "Tone: confident, direct, polite. Clear ask, clear next step, no fluff."
    return "Tone: formal, professional, respectful. Clear structure, not too long."
