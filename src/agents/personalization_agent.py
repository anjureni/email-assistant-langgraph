def personalize(draft: str, profile: dict, sender_name: str) -> str:
    signoff = profile.get("preferred_signoff", "Regards")
    signature_template = profile.get("signature_format", "{sender_name}")
    signature = signature_template.format(sender_name=sender_name)

    out = draft.replace("[SIGNOFF]", signoff).replace("[SIGNATURE]", signature)

    if "[SIGNATURE]" not in draft:
        out = out.rstrip() + f"\n\n{signoff},\n{signature}\n"

    return out
