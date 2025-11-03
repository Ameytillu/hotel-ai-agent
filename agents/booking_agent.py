from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

def booking_response(user_query: str):
    """Handles booking or reservation-related questions."""
    prompt = f"The guest asked: '{user_query}'. Provide an informative and polite response related to hotel bookings or reservations."

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a hotel booking assistant helping guests with availability, reservations, and cancellations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Sorry, I'm having trouble accessing the booking service right now. (Error: {str(e)})"
