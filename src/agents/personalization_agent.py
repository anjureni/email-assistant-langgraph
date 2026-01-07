def personalize(draft: str, profile: dict) -> str:
    signoff = profile.get("preferred_signoff", "Best regards")
    signature = profile.get("signature", "Your Name")

    out = draft.replace("[SIGNOFF]", signoff).replace("[SIGNATURE]", signature)

    # If placeholders missing, append signature
    if "[SIGNATURE]" not in draft:
        out = out.rstrip() + f"\n\n{signoff},\n{signature}\n"
    return out
