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
