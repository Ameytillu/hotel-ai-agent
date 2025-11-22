"""Speech-to-text and text-to-speech helpers for the voice backend."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import BinaryIO, Dict, Optional

from openai import OpenAI

from agents.router_agent import route_to_agent
from hotel_voice_integration.intent_classifier import SUPPORTED_INTENTS, classify_intent
from utils.review_utils import clean_text

VOICE_STT_MODEL = os.getenv("VOICE_STT_MODEL", "gpt-4o-mini-transcribe")
VOICE_TTS_MODEL = os.getenv("VOICE_TTS_MODEL", "gpt-4o-mini-tts")
VOICE_NAME = os.getenv("VOICE_NAME", "alloy")
_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    """Return a singleton OpenAI client for audio operations."""

    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
        _client = OpenAI(api_key=api_key)
    return _client


def _extract_intent(intent_payload: str) -> str:
    """Parse the JSON string returned by :func:`classify_intent`."""

    try:
        payload: Dict[str, str] = json.loads(intent_payload)
    except json.JSONDecodeError:
        return "general_question"

    intent = payload.get("intent", "general_question")
    if intent not in SUPPORTED_INTENTS:
        intent = "general_question"
    return intent


def generate_agent_response(user_text: str) -> str:
    """Return the AI response after cleaning and routing the user input."""

    cleaned_input = clean_text(user_text or "")
    intent_payload = classify_intent(cleaned_input)
    intent = _extract_intent(intent_payload)
    response_text = route_to_agent(intent, cleaned_input)
    if not isinstance(response_text, str):
        response_text = "" if response_text is None else str(response_text)
    print("Intent Classified:", intent)
    return response_text


def transcribe_audio_file(audio_path: str | Path) -> str:
    """Transcribe an audio file using the configured OpenAI STT model."""

    client = _get_client()
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model=VOICE_STT_MODEL,
            file=audio_file,
        )
    text = getattr(transcription, "text", "")
    return text.strip()


def transcribe_audio_stream(audio_stream: BinaryIO) -> str:
    """Transcribe an in-memory audio stream (e.g., direct upload from Twilio)."""

    client = _get_client()
    transcription = client.audio.transcriptions.create(
        model=VOICE_STT_MODEL,
        file=audio_stream,
    )
    text = getattr(transcription, "text", "")
    return text.strip()


def synthesize_speech(text: str, output_path: str | Path) -> Path:
    """Generate a speech file for the given text and return its path."""

    client = _get_client()
    response = client.audio.speech.create(
        model=VOICE_TTS_MODEL,
        voice=VOICE_NAME,
        input=text,
    )
    output_path = Path(output_path)
    audio_bytes = getattr(response, "audio", b"")
    output_path.write_bytes(audio_bytes)
    return output_path
