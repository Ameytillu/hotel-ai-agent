from openai import OpenAI
from dotenv import load_dotenv
import os, pandas as pd

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

def restaurant_response(user_query: str):
    """Fetches menu info from restaurant.csv or uses OpenAI fallback."""
    try:
        df = pd.read_csv("data/restaurant.csv")
    except FileNotFoundError:
        df = pd.DataFrame()

    match = df[df['item'].str.contains(user_query, case=False, na=False)] if 'item' in df else None

    if match is not None and not match.empty:
        row = match.iloc[0]
        info = f"{row['item']} ({row['meal_type']}): {row['description']}, priced at ${row['price']}"
        prompt = f"Guest asked: {user_query}\nMenu item found: {info}\nRespond warmly like a restaurant server."
    else:
        prompt = f"The guest asked: '{user_query}'. No exact menu match found. Provide a friendly restaurant-style answer."

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a hotel restaurant assistant providing menu information and dining recommendations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Sorry, I'm having trouble accessing the restaurant service right now. (Error: {str(e)})"
