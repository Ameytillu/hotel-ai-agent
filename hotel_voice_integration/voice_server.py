import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


"""
voice_server.py
================

This module implements a simple voice interface for your hotel concierge
system.  It exposes two Flask endpoints (`/voice` and `/process`) that
integrate with Twilio's Programmable Voice product to handle inbound
phone calls.  When a call arrives Twilio requests the `/voice`
endpoint, which returns TwiML to greet the caller and prompt for
speech.  Twilio transcribes the caller’s utterance and posts the
transcript to `/process`.  The transcript is routed through the
classification logic to select one of your specialised agents (faq,
booking, restaurant, spa, shuttle or policy), and the agent’s
response is returned as a spoken reply.  Multi‑turn flows such as
hotel bookings are supported by tracking state in a simple in‑memory
session dictionary keyed by the Twilio Call SID.

This file is independent of your Streamlit front end; it imports the
classification and agent functions directly from your existing
project without depending on `streamlit.session_state`.  It should be
safe to drop into the root of your project.  To run locally, you
will need to install `flask` and `twilio` (see requirements below).

Dependencies:

    flask>=2.0
    twilio>=8.0
    openai>=1.0

Environment variables:

    OPENAI_API_KEY – your OpenAI API key for classification
    MODEL_NAME – optional; defaults to "gpt-4o-mini"

Usage:

    export FLASK_APP=hotel_voice_integration/voice_server.py
    flask run --host=0.0.0.0 --port=8000

Expose your server with a tunnelling service such as ngrok and
configure your Twilio phone number’s Voice webhook to point to
`https://<your-ngrok-domain>/voice`.  See README.md for full
instructions.
"""

import os
from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from openai import OpenAI

from agents.faq_agent import faq_answer
from agents.booking_agent import booking_agent
from agents.restaurant_agent import restaurant_response
from agents.spa_agent import spa_response
from agents.policy_agent import policy_response
from agents.shuttle_agent import shuttle_response

app = Flask(__name__)

# Initialise OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

# Keep session state per call in memory.  Keys are Twilio CallSid.
sessions = {}


def classify_intent(text: str) -> str:
    """Classify a user utterance into one of the supported
    categories using an OpenAI Chat completion.  Returns a lowercase
    category name such as 'faq', 'booking', 'restaurant', 'spa',
    'shuttle' or 'policy'.  If classification fails, defaults to
    'faq'.  The model is deterministic (temperature 0) to ensure
    predictable routing.
    """
    prompt = f"""
Classify the user's intent into one of these categories: [FAQ, Booking, Restaurant, Spa, Shuttle, Policy].
Query: "{text}"
Respond with ONLY one word (the category name).
"""
    try:
        result = openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a classification assistant for hotel queries."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        intent = result.choices[0].message.content.strip().lower()
        return intent
    except Exception:
        # Fallback to FAQ if classification fails
        return "faq"


def handle_message(call_id: str, text: str) -> str:
    """Route the caller's message to the appropriate agent and
    return the response.  Maintains a simple session dictionary
    allowing multi‑turn flows for the booking agent.  The booking
    agent maintains its own state across turns, so once a user
    triggers a booking intent the session’s `active_agent` field is
    set to "booking" until the booking agent indicates completion.
    """
    # Ensure a session entry exists
    session = sessions.setdefault(call_id, {"active_agent": None})
    active = session.get("active_agent")

    # If a multi‑turn flow is in progress, continue with that agent
    if active == "booking":
        reply = booking_agent(text)
        # Booking agent should determine when to end flow; here we
        # reset active_agent based on a simple keyword heuristic
        if any(word in text.lower() for word in ["thank", "done", "cancel"]):
            session["active_agent"] = None
        return reply

    # Otherwise classify and route
    intent = classify_intent(text)
    if "faq" in intent:
        return faq_answer(text)
    if "booking" in intent:
        session["active_agent"] = "booking"
        return booking_agent(text)
    if "restaurant" in intent:
        return restaurant_response(text)
    if "spa" in intent:
        return spa_response(text)
    if "shuttle" in intent:
        return shuttle_response(text)
    if "policy" in intent:
        return policy_response(text)
    # Default fallback
    return faq_answer(text)


@app.route("/voice", methods=["GET", "POST"])
def voice() -> str:
    """Initial voice endpoint for Twilio.  Greets the caller and
    prompts for speech.  Twilio will post the transcription to
    `/process` in the same session.
    """
    resp = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/process",
        method="POST",
        language="en-US",
        timeout=5,
        speech_timeout="auto",
    )
    gather.say("Welcome to the Hotel Concierge AI. How may I assist you today?", voice="alice", language="en-US")
    resp.append(gather)
    resp.say("Sorry, I didn't hear anything. Please call again. Goodbye.")
    resp.hangup()
    return str(resp)


@app.route("/process", methods=["GET", "POST"])
def process() -> str:
    """Handle the transcript returned by Twilio.  Uses the CallSid
    as a session identifier to support multi‑turn flows.  Replies
    with the agent’s response and gathers further input if the
    conversation should continue.
    """
    transcript = request.values.get("SpeechResult", "") or request.values.get("speechResult", "")
    call_id = request.values.get("CallSid", "")
    # Generate reply using our routing logic
    reply = handle_message(call_id, transcript)
    # Build TwiML response
    resp = VoiceResponse()
    # Speak the reply
    resp.say(reply, voice="alice", language="en-US")
    # Determine if conversation should continue
    if any(word in transcript.lower() for word in ["bye", "goodbye", "thank you"]):
        resp.hangup()
        return str(resp)
    # Prompt for further input
    gather = Gather(
        input="speech",
        action="/process",
        method="POST",
        language="en-US",
        timeout=5,
        speech_timeout="auto",
    )
    gather.say("Is there anything else I can help you with?", voice="alice", language="en-US")
    resp.append(gather)
    return str(resp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)