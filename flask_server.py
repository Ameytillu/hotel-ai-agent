import os

from dotenv import load_dotenv
from flask import Flask, Request, Response, request
from twilio.twiml.voice_response import VoiceResponse, Gather

# Local utilities
from utils.stt_tts_utils import process_speech_and_generate_audio

load_dotenv()
app = Flask(__name__)


def _extract_speech(req: Request) -> str:
    """
    Pull the caller's spoken text from the Twilio POST body.
    Twilio usually sends it in `SpeechResult`; fall back to empty string.
    """
    return (req.values.get("SpeechResult") or "").strip()


def _build_twiml_response(text: str) -> str:
    """Convert a text reply into TwiML that Twilio can speak."""
    vr = VoiceResponse()
    vr.say(
        text,
        voice=os.getenv("TWILIO_VOICE", "Polly.Joanna"),
        language=os.getenv("TWILIO_LANGUAGE", "en-US"),
    )
    return str(vr)


def _append_gather(resp: VoiceResponse, prompt: str) -> None:
    """
    Attach a <Gather> block that listens for speech and posts it to /process.
    Keeps the call open for multi-turn conversations.
    """
    gather: Gather = resp.gather(
        input="speech",
        action="/process",
        method="POST",
        speech_timeout="auto",
        timeout=5,
        language=os.getenv("TWILIO_LANGUAGE", "en-US"),
    )
    gather.say(
        prompt,
        voice=os.getenv("TWILIO_VOICE", "Polly.Joanna"),
        language=os.getenv("TWILIO_LANGUAGE", "en-US"),
    )


def _should_end_conversation(user_text: str) -> bool:
    """
    Simple heuristic to end the call if the caller says goodbye/thanks.
    """
    lowered = user_text.lower()
    return any(keyword in lowered for keyword in ["bye", "goodbye", "thank", "thanks", "nothing"])


@app.route("/voice", methods=["GET", "POST"])
def voice() -> Response:
    """
    Main webhook Twilio hits after gathering speech.
    - Get the caller transcript
    - Kick off the first gather so the caller can speak
    """
    resp = VoiceResponse()
    _append_gather(
        resp,
        "Welcome to the Hotel Concierge AI. How may I assist you today?",
    )
    resp.say("Sorry, I didn't receive any input. Please call again. Goodbye.")
    resp.hangup()
    return Response(str(resp), mimetype="text/xml")


@app.route("/process", methods=["GET", "POST"])
def process() -> Response:
    """
    (Optional second stage if you use a Gather -> /process flow)
    Mirrors /voice so Twilio can repost follow-up speech.
    """
    user_input = _extract_speech(request) or "Hello"
    reply_text = process_speech_and_generate_audio(user_input)
    resp = VoiceResponse()
    resp.say(
        reply_text,
        voice=os.getenv("TWILIO_VOICE", "Polly.Joanna"),
        language=os.getenv("TWILIO_LANGUAGE", "en-US"),
    )

    if _should_end_conversation(user_input):
        resp.say("Thank you for calling. Goodbye!")
        resp.hangup()
    else:
        _append_gather(resp, "Is there anything else I can help you with?")
    return Response(str(resp), mimetype="text/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
