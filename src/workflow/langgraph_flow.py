import json
import re
from datetime import datetime
from typing import TypedDict, Dict, Any

from langgraph.graph import StateGraph, END

from src.agents.input_parser_agent import run_input_parser
from src.agents.intent_detection_agent import detect_intent
from src.agents.tone_stylist_agent import tone_instructions
from src.agents.draft_writer_agent import write_draft
from src.agents.personalization_agent import personalize
from src.agents.review_agent import review_email
from src.agents.router_agent import needs_retry

PROFILE_PATH = "src/memory/user_profiles.json"

# -----------------------------
# Config
# -----------------------------
MAX_RETRIES = 3            # ✅ retry up to 3 times
MAX_HISTORY = 10           # ✅ store last 10 interactions

# ✅ guardrails: edit this list based on what you want to block
BLOCKLIST_WORDS = [
    "password",
    "ssn",
    "social security",
    "credit card",
    "bank account",
    "wire transfer",
    "phishing",
    "hack",
]


# -----------------------------
# State
# -----------------------------
class EmailState(TypedDict):
    raw: Dict[str, Any]
    parsed: Dict[str, Any]
    profile: Dict[str, Any]
    profile_key: str

    intent: str
    tone_rules: str
    draft: str
    personalized: str
    reviewed: str
    final: str

    retries: int

    # guardrails fields
    guardrails: Dict[str, Any]
    blocked: bool


# -----------------------------
# Profile / Memory helpers
# -----------------------------
def _load_all_profiles() -> Dict[str, Any]:
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_all_profiles(data: Dict[str, Any]) -> None:
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_profile(key: str = "formal") -> Dict[str, Any]:
    data = _load_all_profiles()

    # fallback order: requested key -> "formal" -> first profile in file
    if key in data:
        prof = data[key]
    elif "formal" in data:
        prof = data["formal"]
    else:
        prof = next(iter(data.values()))

    # ensure expected fields exist
    prof.setdefault("prompt_history", [])
    prof.setdefault("last_drafts", [])
    prof.setdefault("conversation_history", [])  # ✅ last 10 full interactions
    return prof


def save_draft(key: str, final_email: str) -> None:
    data = _load_all_profiles()
    prof = data.get(key) or data.get("formal") or next(iter(data.values()))

    drafts = prof.get("last_drafts", [])
    drafts.append(final_email)
    prof["last_drafts"] = drafts[-5:]  # keep last 5 drafts

    data[key] = prof
    _save_all_profiles(data)


def append_prompt_history(key: str, prompt: str) -> None:
    """Keeps only the last 10 prompts."""
    if not prompt:
        return

    data = _load_all_profiles()
    prof = data.get(key) or data.get("formal") or next(iter(data.values()))

    history = prof.get("prompt_history", [])
    history.append(prompt)
    prof["prompt_history"] = history[-10:]

    data[key] = prof
    _save_all_profiles(data)


def append_conversation_history(
    key: str,
    *,
    prompt: str,
    tone: str,
    intent: str,
    final_email: str,
    retries: int,
    blocked: bool,
    guardrails_reason: str = "",
) -> None:
    """✅ Stores last 10 full interactions."""
    data = _load_all_profiles()
    prof = data.get(key) or data.get("formal") or next(iter(data.values()))

    conv = prof.get("conversation_history", [])
    conv.append(
        {
            "ts": datetime.utcnow().isoformat() + "Z",
            "prompt": prompt,
            "tone": tone,
            "intent": intent,
            "final": final_email,
            "retries": retries,
            "blocked": blocked,
            "guardrails_reason": guardrails_reason,
        }
    )
    prof["conversation_history"] = conv[-MAX_HISTORY:]

    data[key] = prof
    _save_all_profiles(data)


def _contains_blocked(text: str) -> bool:
    t = (text or "").lower()
    return any(w.lower() in t for w in BLOCKLIST_WORDS)


def purge_blocked_memory(key: str) -> None:
    """
    ✅ Remove ONLY entries that contain blocked words from:
    - prompt_history
    - conversation_history (prompt/final)
    - last_drafts
    Keeps everything else.
    """
    data = _load_all_profiles()
    prof = data.get(key) or data.get("formal") or next(iter(data.values()))

    # 1) prompt_history
    ph = prof.get("prompt_history", [])
    prof["prompt_history"] = [p for p in ph if not _contains_blocked(p)][-10:]

    # 2) conversation_history
    ch = prof.get("conversation_history", [])
    cleaned_ch = []
    for e in ch:
        prompt = e.get("prompt", "")
        final = e.get("final", "")
        if _contains_blocked(prompt) or _contains_blocked(final):
            continue
        cleaned_ch.append(e)
    prof["conversation_history"] = cleaned_ch[-MAX_HISTORY:]

    # 3) last_drafts ✅ IMPORTANT
    ld = prof.get("last_drafts", [])
    prof["last_drafts"] = [d for d in ld if not _contains_blocked(d)][-5:]

    data[key] = prof
    _save_all_profiles(data)


# -----------------------------
# Guardrails
# -----------------------------
def guardrails_check(text: str) -> Dict[str, Any]:
    """
    Simple guardrails:
    - Blocklist words
    - Simple SSN-like pattern
    """
    t = (text or "").lower()

    for w in BLOCKLIST_WORDS:
        if w.lower() in t:
            return {"allowed": False, "reason": f"Blocked content detected: '{w}'"}

    # Optional: SSN-like pattern
    if re.search(r"\b\d{3}-\d{2}-\d{4}\b", t):
        return {"allowed": False, "reason": "Blocked: SSN-like pattern detected"}

    return {"allowed": True, "reason": ""}


SAFE_BLOCK_MESSAGE = (
    "⚠️ Sorry — I can’t generate this email because it may contain sensitive or restricted content. "
    "Please remove sensitive details and try again."
)


# -----------------------------
# Nodes
# -----------------------------
def n_parse(state: EmailState) -> EmailState:
    parsed = run_input_parser(state["raw"])
    state["parsed"] = parsed.model_dump()
    return state


def n_profile(state: EmailState) -> EmailState:
    tone = state["parsed"].get("tone", "formal")
    profile_key = tone if tone in {"formal", "casual", "assertive"} else "formal"
    prof = load_profile(profile_key)

    state["profile_key"] = profile_key
    state["profile"] = prof
    return state


def n_intent(state: EmailState) -> EmailState:
    state["intent"] = detect_intent(state["parsed"].get("prompt", ""))
    return state


def n_tone(state: EmailState) -> EmailState:
    state["tone_rules"] = tone_instructions(state["parsed"].get("tone", "formal"))
    return state


def n_draft(state: EmailState) -> EmailState:
    p = state["parsed"]
    current_prompt = p.get("prompt", "")

    state["draft"] = write_draft(
        intent=state["intent"],
        tone=p.get("tone", "formal"),
        tone_rules=state["tone_rules"],
        prompt=current_prompt,
        recipient_name=p.get("recipient_name"),
        company_name=p.get("company_name"),
        extra_context=p.get("extra_context"),
        length=p.get("length", "medium"),
    )
    return state


def n_personalize(state: EmailState) -> EmailState:
    state["personalized"] = personalize(
        state["draft"],
        state["profile"],
        state["parsed"].get("sender_name", ""),
    )
    return state


def n_guardrails(state: EmailState) -> EmailState:
    """
    ✅ Guardrails runs before review/final.
    If blocked: we stop and finalize with safe message.
    """
    check = guardrails_check(state.get("personalized", ""))
    state["guardrails"] = check
    state["blocked"] = not check.get("allowed", True)
    return state


def route_after_guardrails(state: EmailState) -> str:
    if state.get("blocked", False):
        return "blocked_finalize"
    return "review"


def n_review(state: EmailState) -> EmailState:
    state["reviewed"] = review_email(state["personalized"], state["parsed"].get("tone", "formal"))
    return state


def route_after_review(state: EmailState) -> str:
    """✅ Retry up to MAX_RETRIES times if review says output is bad."""
    if needs_retry(state.get("reviewed", "")) and state.get("retries", 0) < MAX_RETRIES:
        state["retries"] = state.get("retries", 0) + 1
        return "draft"
    return "finalize"


def n_blocked_finalize(state: EmailState) -> EmailState:
    """
    ✅ When guardrails blocks:
    - Return safe message
    - Purge ONLY memory entries containing blocked words
    - Do NOT save this blocked prompt/output to history
    - Reload profile after purge to ensure clean state
    """
    state["final"] = SAFE_BLOCK_MESSAGE

    profile_key = state.get("profile_key", "formal")

    # ✅ clear only entries that contain blocked words; keep everything else
    purge_blocked_memory(profile_key)

    # ✅ reload profile to ensure state is clean for next run
    state["profile"] = load_profile(profile_key)

    # ❌ Do NOT append blocked prompt/history
    return state


def n_finalize(state: EmailState) -> EmailState:
    """
    ✅ Finalize on success path:
    - save draft
    - store prompt_history (last 10 prompts)
    - store conversation_history (last 10 interactions)
    """
    state["final"] = state.get("reviewed", "") or state.get("personalized", "")

    p = state["parsed"]
    profile_key = state.get("profile_key", "formal")
    tone = p.get("tone", "formal")
    prompt = p.get("prompt", "")

    # last_drafts (5)
    save_draft(profile_key, state["final"])

    # prompt history (10)
    append_prompt_history(profile_key, prompt)

    # conversation history (10)
    append_conversation_history(
        profile_key,
        prompt=prompt,
        tone=tone,
        intent=state.get("intent", ""),
        final_email=state["final"],
        retries=state.get("retries", 0),
        blocked=False,
        guardrails_reason="",
    )

    return state


# -----------------------------
# Graph
# -----------------------------
def build_graph():
    g = StateGraph(EmailState)

    g.add_node("parse", n_parse)
    g.add_node("profile", n_profile)
    g.add_node("intent", n_intent)
    g.add_node("tone", n_tone)
    g.add_node("draft", n_draft)
    g.add_node("personalize", n_personalize)
    g.add_node("guardrails", n_guardrails)
    g.add_node("review", n_review)
    g.add_node("finalize", n_finalize)
    g.add_node("blocked_finalize", n_blocked_finalize)

    g.set_entry_point("parse")
    g.add_edge("parse", "profile")
    g.add_edge("profile", "intent")
    g.add_edge("intent", "tone")
    g.add_edge("tone", "draft")
    g.add_edge("draft", "personalize")

    # ✅ Guardrails before review
    g.add_edge("personalize", "guardrails")
    g.add_conditional_edges(
        "guardrails",
        route_after_guardrails,
        {
            "review": "review",
            "blocked_finalize": "blocked_finalize",
        },
    )

    # ✅ Retry logic after review
    g.add_conditional_edges(
        "review",
        route_after_review,
        {"draft": "draft", "finalize": "finalize"},
    )

    g.add_edge("finalize", END)
    g.add_edge("blocked_finalize", END)

    return g.compile()


GRAPH = build_graph()


def generate_email_with_agents(raw: Dict[str, Any]) -> str:
    state: EmailState = {
        "raw": raw,
        "parsed": {},
        "profile": {},
        "profile_key": "formal",
        "intent": "",
        "tone_rules": "",
        "draft": "",
        "personalized": "",
        "reviewed": "",
        "final": "",
        "retries": 0,
        "guardrails": {"allowed": True, "reason": ""},
        "blocked": False,
    }
    out = GRAPH.invoke(state)
    return out["final"]
