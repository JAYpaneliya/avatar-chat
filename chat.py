import os
import json
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from prompt_builder import build_system_prompt
from memory import get_recent_messages, save_message, get_all_messages, clear_messages
from avatar import get_avatar_by_id

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "300"))


def chat_with_avatar(user_id: str, avatar_id: int, user_message: str) -> dict:
    avatar = get_avatar_by_id(avatar_id)
    if not avatar:
        raise ValueError(f"Avatar {avatar_id} not found.")

    system_prompt = build_system_prompt(avatar)
    history = get_recent_messages(user_id, avatar_id)

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=0.85,
    )

    reply = response.choices[0].message.content.strip()

    save_message(user_id, avatar_id, "user", user_message)
    save_message(user_id, avatar_id, "assistant", reply)

    return {"reply": reply, "avatar_name": avatar["name"]}


def analyse_chat(user_id: str, avatar_id: int) -> dict:
    avatar = get_avatar_by_id(avatar_id)
    if not avatar:
        raise ValueError(f"Avatar {avatar_id} not found.")

    history = get_all_messages(user_id, avatar_id)
    if len(history) < 2:
        raise ValueError("Not enough messages to analyse. Have at least a short conversation first.")

    # Format conversation for analysis
    convo_text = ""
    for msg in history:
        label = "You" if msg["role"] == "user" else avatar["name"]
        convo_text += f"{label}: {msg['content']}\n"

    analysis_prompt = f"""You are a brutally honest but supportive social skills coach giving direct feedback to someone who just finished a practice chat.

You are talking DIRECTLY to the person — use "you", "your", "you did", "you said" — never say "the user". Speak to them like a coach talking to their student face to face.

They were chatting with their {avatar["relationship"]} named {avatar["name"]} ({avatar.get("age", "young")} years old, {avatar.get("occupation", "")}).

Here is the full conversation:
---
{convo_text}
---

Analyse how THEY performed. Be direct, honest, and reference their actual messages specifically. Talk TO them, not about them.

Return ONLY a valid JSON object in this exact format with no extra text:
{{
  "overall_score": <number 1-10>,
  "summary": "<2-3 sentences talking directly to them — e.g. 'You came in confident but lost steam halfway through...'>",
  "scores": {{
    "confidence": <1-10>,
    "humour": <1-10>,
    "conversation_flow": <1-10>,
    "emotional_intelligence": <1-10>,
    "authenticity": <1-10>
  }},
  "score_explanations": {{
    "confidence": "<talk directly to them — e.g. 'You hesitated when she went cold instead of holding your ground'>",
    "humour": "<talk directly to them>",
    "conversation_flow": "<talk directly to them>",
    "emotional_intelligence": "<talk directly to them>",
    "authenticity": "<talk directly to them>"
  }},
  "what_went_well": ["<start with You — e.g. 'You opened strong with a confident opener'>", "<another thing you did well>"],
  "what_to_improve": ["<start with You — e.g. 'You went too available too fast when she took time to reply'>", "<another thing to work on>"],
  "her_impression": "<how would {avatar["name"]} actually feel about you after this conversation? be honest and direct — e.g. 'She probably found you sweet but a little too eager...'>",
  "tip_for_next_time": "<one very specific actionable tip based on THIS conversation — talk directly to them, e.g. 'Next time she goes cold, dont double text — hold your ground and let her come back'>"
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": analysis_prompt}],
        max_tokens=1000,
        temperature=0.4,
    )

    raw = response.choices[0].message.content.strip()

    # Clean up if model wraps in markdown code block
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)

    # Clear messages after analysis so next session starts fresh
    clear_messages(user_id, avatar_id)

    return result