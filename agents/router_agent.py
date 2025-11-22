from openai import OpenAI
from dotenv import load_dotenv
import os
import streamlit as st

from agents.faq_agent import faq_answer
from agents.booking_agent import booking_agent
from agents.restaurant_agent import restaurant_response
from agents.spa_agent import spa_response
from agents.policy_agent import policy_response
from agents.shuttle_agent import shuttle_response

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

def route_query(user_query: str):
    """
    The 'brain' of your concierge system.
    Decides which specialized agent should handle the guest query.
    """

    if "active_agent" not in st.session_state:
        st.session_state.active_agent = None

    # --- Context memory: stay in the same flow ---
    if st.session_state.active_agent == "booking":
        return booking_agent(user_query)
"""Main router agent that dispatches guest intents to specialized handlers."""

from __future__ import annotations

from typing import Callable, Dict

from agents import (
    booking_agent,
    faq_agent,
    restaurant_agent,
    spa_agent,
    shuttle_agent,
    sentiment_agent,
    policy_agent,
)

Handler = Callable[[str], str]


def _ensure_string(response: object) -> str:
    """Convert the agent response to a string."""

    if isinstance(response, str):
        return response
    return "" if response is None else str(response)


def _handle_booking_request(user_message: str) -> str:
    handler = getattr(booking_agent, "handle", None)
    if callable(handler):
        return _ensure_string(handler(user_message))

    fallback = getattr(booking_agent, "booking_agent", None)
    if callable(fallback):
        return _ensure_string(fallback(user_message))

    return "I can assist with bookings once the booking agent is configured."


def _handle_room_upgrade(user_message: str) -> str:
    handler = getattr(booking_agent, "handle_upgrade", None)
    if callable(handler):
        return _ensure_string(handler(user_message))

    return _handle_booking_request(user_message)


def _handle_complaint(user_message: str) -> str:
    handler = getattr(policy_agent, "handle_complaint", None)
    if callable(handler):
        return _ensure_string(handler(user_message))

    policy_handler = getattr(policy_agent, "policy_response", None)
    if callable(policy_handler):
        return _ensure_string(policy_handler(user_message))

    return _handle_feedback_review(user_message)


def _handle_general_question(user_message: str) -> str:
    return _ensure_string(faq_agent.faq_answer(user_message))


def _handle_restaurant(user_message: str) -> str:
    return _ensure_string(restaurant_agent.restaurant_response(user_message))


def _handle_spa(user_message: str) -> str:
    return _ensure_string(spa_agent.spa_response(user_message))


def _handle_shuttle(user_message: str) -> str:
    return _ensure_string(shuttle_agent.shuttle_response(user_message))


def _handle_feedback_review(user_message: str) -> str:
    handler = getattr(sentiment_agent, "handle", None)
    if callable(handler):
        return _ensure_string(handler(user_message))

    review_handler = getattr(sentiment_agent, "respond_to_review", None)
    if callable(review_handler):
        return _ensure_string(review_handler(user_message))

    analyzer = getattr(sentiment_agent, "analyze_sentiment", None)
    if callable(analyzer):
        sentiment = analyzer(user_message)
        if sentiment.lower() == "negative":
            return "We’re sorry you had a bad experience. Our team will contact you shortly."
        return "Thank you for sharing your feedback with us!"

    return _handle_general_question(user_message)


INTENT_DISPATCH: Dict[str, Handler] = {
    "booking_request": _handle_booking_request,
    "complaint": _handle_complaint,
    "general_question": _handle_general_question,
    "restaurant_inquiry": _handle_restaurant,
    "spa_request": _handle_spa,
    "shuttle_request": _handle_shuttle,
    "feedback_review": _handle_feedback_review,
    "room_upgrade_inquiry": _handle_room_upgrade,
}


def route_to_agent(intent: str, user_message: str) -> str:
    """Route the user message to the agent that can handle the provided intent."""

    normalized_intent = (intent or "").strip().lower()
    handler = INTENT_DISPATCH.get(normalized_intent, _handle_general_question)

    try:
        classification_prompt = f"""
        Classify the user's intent into one of these categories:
        [FAQ, Booking, Restaurant, Spa, Shuttle, Policy]
        Query: "{user_query}"

        Respond with ONLY one word (the category name).
        """

        classification = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a classification assistant for hotel queries."},
                {"role": "user", "content": classification_prompt}
            ],
            temperature=0,
        return handler(user_message)
    except Exception as exc:  # pragma: no cover - defensive fallback
        return _handle_general_question(
            f"We encountered an issue while processing your request ({exc}). Could you rephrase?"
        )

        intent = classification.choices[0].message.content.strip().lower()
        print(f"[Router] Detected intent → {intent}")

        if "faq" in intent:
            return faq_answer(user_query)
        elif "booking" in intent:
            st.session_state.active_agent = "booking"  # remember session
            return booking_agent(user_query)
        elif "restaurant" in intent:
            return restaurant_response(user_query)
        elif "spa" in intent:
            return spa_response(user_query)
        elif "shuttle" in intent:
            return shuttle_response(user_query)
        elif "policy" in intent:
            return policy_response(user_query)
        else:
            return faq_answer(user_query)

    except Exception as e:
        return f"⚠️ Router Error: {str(e)}"