import json
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

class EmailState(TypedDict):
    raw: Dict[str, Any]
    parsed: Dict[str, Any]
    profile: Dict[str, Any]
    intent: str
    tone_rules: str
    draft: str
    personalized: str
    reviewed: str
    final: str
    retries: int

def load_profile(key: str = "formal") -> Dict[str, Any]:
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # fallback order: requested key -> "formal" -> first profile in file
    if key in data:
        return data[key]
    if "formal" in data:
        return data["formal"]
    return next(iter(data.values()))


def save_draft(key: str, final_email: str) -> None:
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    prof = data.get(key) or data.get("formal") or next(iter(data.values()))
    drafts = prof.get("last_drafts", [])
    drafts.append(final_email)
    prof["last_drafts"] = drafts[-5:]
    data[key] = prof
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def n_parse(state: EmailState) -> EmailState:
    parsed = run_input_parser(state["raw"])
    state["parsed"] = parsed.model_dump()
    return state

def n_profile(state: EmailState) -> EmailState:
    tone = state["parsed"]["tone"]
    profile_key = tone if tone in {"formal", "casual", "assertive"} else "formal"
    state["profile"] = load_profile(profile_key)
    return state

def n_intent(state: EmailState) -> EmailState:
    state["intent"] = detect_intent(state["parsed"]["prompt"])
    return state

def n_tone(state: EmailState) -> EmailState:
    state["tone_rules"] = tone_instructions(state["parsed"]["tone"])
    return state

def n_draft(state: EmailState) -> EmailState:
    p = state["parsed"]
    state["draft"] = write_draft(
        intent=state["intent"],
        tone_rules=state["tone_rules"],
        prompt=p["prompt"],
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
    state["parsed"]["sender_name"]
    )
    return state

def n_review(state: EmailState) -> EmailState:
    state["reviewed"] = review_email(state["personalized"], state["parsed"]["tone"])
    return state

def n_finalize(state: EmailState) -> EmailState:
    state["final"] = state["reviewed"]
    # save to the same profile we loaded (based on tone)
    tone = state["parsed"]["tone"]
    profile_key = tone if tone in {"formal", "casual", "assertive"} else "formal"
    save_draft(profile_key, state["final"])
    return state

def route_after_review(state: EmailState) -> str:
    # retry drafting once if output looks bad
    if needs_retry(state.get("reviewed", "")) and state.get("retries", 0) < 1:
        state["retries"] = state.get("retries", 0) + 1
        return "draft"
    return "finalize"

def build_graph():
    g = StateGraph(EmailState)
    g.add_node("parse", n_parse)
    g.add_node("profile", n_profile)
    g.add_node("intent", n_intent)
    g.add_node("tone", n_tone)
    g.add_node("draft", n_draft)
    g.add_node("personalize", n_personalize)
    g.add_node("review", n_review)
    g.add_node("finalize", n_finalize)

    g.set_entry_point("parse")
    g.add_edge("parse", "profile")
    g.add_edge("profile", "intent")
    g.add_edge("intent", "tone")
    g.add_edge("tone", "draft")
    g.add_edge("draft", "personalize")
    g.add_edge("personalize", "review")
    g.add_conditional_edges("review", route_after_review, {"draft": "draft", "finalize": "finalize"})
    g.add_edge("finalize", END)
    return g.compile()

GRAPH = build_graph()

def generate_email_with_agents(raw: Dict[str, Any]) -> str:
    state: EmailState = {
        "raw": raw,
        "parsed": {},
        "profile": {},
        "intent": "",
        "tone_rules": "",
        "draft": "",
        "personalized": "",
        "reviewed": "",
        "final": "",
        "retries": 0,
    }
    out = GRAPH.invoke(state)
    return out["final"]