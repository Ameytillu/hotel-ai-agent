"""Main router agent that dispatches guest intents to specialized handlers."""

from __future__ import annotations

from typing import Callable, Dict
from openai import OpenAI
from dotenv import load_dotenv
import os

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

from agents.faq_agent import faq_answer
from agents.booking_agent import booking_agent
from agents.restaurant_agent import restaurant_response
from agents.spa_agent import spa_response
from agents.policy_agent import policy_response
from agents.shuttle_agent import shuttle_response

try:
    from agents import sentiment_agent
    HAS_SENTIMENT = True
except ImportError:
    HAS_SENTIMENT = False

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

Handler = Callable[[str], str]


def _ensure_string(response: object) -> str:
    """Convert the agent response to a string."""
    if isinstance(response, str):
        return response
    return "" if response is None else str(response)


def _handle_booking_request(user_message: str) -> str:
    return _ensure_string(booking_agent(user_message))


def _handle_room_upgrade(user_message: str) -> str:
    return _handle_booking_request(user_message)


def _handle_complaint(user_message: str) -> str:
    return _ensure_string(policy_response(user_message))


def _handle_general_question(user_message: str) -> str:
    return _ensure_string(faq_answer(user_message))


def _handle_restaurant(user_message: str) -> str:
    return _ensure_string(restaurant_response(user_message))


def _handle_spa(user_message: str) -> str:
    return _ensure_string(spa_response(user_message))


def _handle_shuttle(user_message: str) -> str:
    return _ensure_string(shuttle_response(user_message))


def _handle_feedback_review(user_message: str) -> str:
    if HAS_SENTIMENT:
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
                return "We're sorry you had a bad experience. Our team will contact you shortly."
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
        return handler(user_message)
    except Exception as exc:
        return _handle_general_question(
            f"We encountered an issue while processing your request. Could you rephrase?"
        )


def route_query(user_query: str):
    """
    The 'brain' of your concierge system.
    Decides which specialized agent should handle the guest query.
    Supports both Streamlit and non-Streamlit environments (Flask, voice calls, SMS).
    """
    
    # Handle session state for Streamlit
    if HAS_STREAMLIT:
        if "active_agent" not in st.session_state:
            st.session_state.active_agent = None

        # --- Context memory: stay in the same flow ---
        if st.session_state.active_agent == "booking":
            return booking_agent(user_query)

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
        )

        intent = classification.choices[0].message.content.strip().lower()
        print(f"[Router] Detected intent → {intent}")

        if "faq" in intent:
            return faq_answer(user_query)
        elif "booking" in intent:
            if HAS_STREAMLIT:
                st.session_state.active_agent = "booking"
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
