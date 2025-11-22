# hotel_voice_integration/stt_tts_utils.py

import os
from dotenv import load_dotenv
from openai import OpenAI
from utils.review_utils import clean_text


# Load API keys from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def process_speech_and_generate_audio(user_input):
    """
    This function takes the user's speech (text from Twilio),
    cleans it, sends it to OpenAI, and returns AI-generated text.
    Twilio will speak this text back to the caller.
    """

    if not user_input or user_input.strip() == "":
        user_input = "Hello"

    cleaned_input = clean_text(user_input)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful hotel concierge. Keep your answers short and friendly."},
            {"role": "user", "content": cleaned_input}
        ]
    )

    ai_text = response.choices[0].message.content
    return ai_text
