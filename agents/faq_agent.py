from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

def faq_answer(user_query: str):
    """Answers hotel FAQs using local FAQ data and OpenAI for fallback."""
    try:
        # Load FAQ data
        faq_path = "rag_data/hotel_faq.json"
        if os.path.exists(faq_path):
            with open(faq_path, "r", encoding="utf-8") as f:
                faq_data = json.load(f)
        else:
            faq_data = []

        # Check for a match
        match = next(
            (faq for faq in faq_data if user_query.lower() in faq["question"].lower()), 
            None
        )

        if match:
            prompt = f"The guest asked: '{user_query}'.\nUse this info:\nQ: {match['question']}\nA: {match['answer']}\nReply politely."
        else:
            prompt = f"The guest asked: '{user_query}'. Please provide a helpful hotel-style FAQ response."

        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a polite hotel concierge answering guest FAQs clearly and warmly."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Sorry, I couldn’t fetch the FAQ response. (Error: {str(e)})"
