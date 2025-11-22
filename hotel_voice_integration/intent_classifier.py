"""Guest intent classification utilities for the voice integration layer."""

from __future__ import annotations

import json
import os
from typing import Dict

from openai import OpenAI

SUPPORTED_INTENTS = [
    "booking_request",
    "complaint",
    "general_question",
    "restaurant_inquiry",
    "spa_request",
    "shuttle_request",
    "feedback_review",
    "room_upgrade_inquiry",
]

MODEL_NAME = os.getenv("INTENT_CLASSIFIER_MODEL", "gpt-4o-mini")
_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Return a cached OpenAI client."""

    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
        _client = OpenAI(api_key=api_key)
    return _client


def _extract_json_object(raw_response: str) -> Dict[str, str]:
    """Parse the JSON object from the model response safely."""

    if not raw_response:
        return {"intent": "general_question"}

    cleaned = raw_response.strip()
    if "```" in cleaned:
        cleaned = cleaned.strip("`\n")
        if "{" in cleaned:
            cleaned = cleaned[cleaned.index("{") :]
        if "}" in cleaned:
            cleaned = cleaned[: cleaned.rindex("}") + 1]
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        payload = {"intent": "general_question"}

    intent = payload.get("intent", "general_question")
    if intent not in SUPPORTED_INTENTS:
        intent = "general_question"
    payload["intent"] = intent
    return payload


def classify_intent(user_message: str) -> str:
    """Classify the user's intent using GPT and return a strict JSON string."""

    sanitized_message = (user_message or "").strip()
    if not sanitized_message:
        return json.dumps({"intent": "general_question"})

    client = _get_client()
    system_prompt = (
        "You are an intent classification assistant for a hotel concierge system. "
        "Respond ONLY with a JSON object containing the key 'intent'. Valid "
        "intents are: "
        + ", ".join(SUPPORTED_INTENTS)
        + ". If unsure, reply with general_question."
    )

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": sanitized_message},
        ],
    )

    raw = completion.choices[0].message.content if completion.choices else ""
    payload = _extract_json_object(raw)
    return json.dumps(payload)