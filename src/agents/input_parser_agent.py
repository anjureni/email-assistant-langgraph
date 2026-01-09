from pydantic import BaseModel, Field
from typing import Optional

class ParsedInput(BaseModel):
    prompt: str = Field(..., min_length=5)
    tone: str = "formal"
    sender_name: str
    recipient_name: Optional[str] = None
    company_name: Optional[str] = None
    extra_context: Optional[str] = None
    length: str = "medium"
    

def run_input_parser(raw: dict) -> ParsedInput:
    tone = (raw.get("tone") or "formal").lower().strip()
    if tone not in {"formal", "casual", "assertive"}:
        tone = "formal"

    length = (raw.get("length") or "medium").lower().strip()
    if length not in {"short", "medium", "long"}:
        length = "medium"

   

    return ParsedInput(
        prompt=(raw.get("prompt") or "").strip(),
        tone=tone,
        sender_name=(raw.get("sender_name") or "Your Name"),
        recipient_name=(raw.get("recipient_name") or None),
        company_name=(raw.get("company_name") or None),
        extra_context=(raw.get("extra_context") or None),
        length=length,
      
    )
