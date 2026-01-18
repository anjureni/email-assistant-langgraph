import streamlit as st
import json
import os

PROFILE_PATH = os.path.join("src", "memory", "user_profiles.json")

def get_all_prompt_histories():
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        histories = {}
        for key, prof in data.items():
            histories[key] = prof.get("prompt_history", [])
        return histories
    except Exception:
        return {}

st.set_page_config(page_title="Prompt History", layout="wide")
st.title("🕑 Prompt History")

histories = get_all_prompt_histories()

has_any_history = any(prompts for prompts in histories.values())

if not has_any_history:
    st.info("No prompt history found for any profile.")
else:
    for profile, prompts in histories.items():
        st.subheader(f"Profile: {profile}")
        if prompts:
            for i, h in enumerate(prompts[-10:], 1):
                st.markdown(f"**{i}.** {h}")
        else:
            st.markdown("_No prompts for this profile._")
