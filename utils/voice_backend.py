"""High-level helpers that orchestrate the voice processing workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from hotel_voice_integration import stt_tts_utils


def process_text_message(user_message: str) -> str:
    """Process a plain text chat/voice message and return the agent's reply."""

    return stt_tts_utils.generate_agent_response(user_message)


def process_twilio_payload(payload: Dict[str, Any], *, playback: bool = False,
                           audio_output: Optional[str] = None) -> Dict[str, str]:
    """Handle a Twilio Voice payload containing either speech or text input."""

    transcript = (
        payload.get("SpeechResult")
        or payload.get("speech_result")
        or payload.get("Body")
        or payload.get("text")
        or ""
    )
    response_text = stt_tts_utils.generate_agent_response(transcript)

    response: Dict[str, str] = {"response_text": response_text}
    if playback:
        output_path = audio_output or "twilio_response.mp3"
        audio_file = stt_tts_utils.synthesize_speech(response_text, output_path)
        response["audio_file"] = str(audio_file)
    return response


def process_audio_file(audio_path: str | Path, *, playback: bool = False,
                       audio_output: Optional[str] = None) -> Dict[str, str]:
    """Transcribe a saved audio file, route the intent, and optionally produce TTS."""

    transcript = stt_tts_utils.transcribe_audio_file(audio_path)
    response_text = stt_tts_utils.generate_agent_response(transcript)

    response: Dict[str, str] = {
        "transcript": transcript,
        "response_text": response_text,
    }
    if playback:
        output_path = audio_output or "call_response.mp3"
        audio_file = stt_tts_utils.synthesize_speech(response_text, output_path)
        response["audio_file"] = str(audio_file)
    return response