def needs_retry(text: str) -> bool:
    if not text:
        return True
    if "Subject:" not in text:
        return True
    if len(text) < 120:
        return True
    return False
