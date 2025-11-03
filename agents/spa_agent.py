from openai import OpenAI
from dotenv import load_dotenv
import os, pandas as pd

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

def spa_response(user_query: str):
    """Provides spa service details from spa.csv or fallback via API."""
    try:
        df = pd.read_csv("data/spa.csv")
    except FileNotFoundError:
        df = pd.DataFrame()

    match = df[df['service_name'].str.contains(user_query, case=False, na=False)] if 'service_name' in df else None

    if match is not None and not match.empty:
        row = match.iloc[0]
        info = f"{row['service_name']}: {row['description']}, priced at ${row['price']}"
        prompt = f"Guest asked: {user_query}\nService found: {info}\nRespond politely like a spa receptionist."
    else:
        prompt = f"The guest asked: '{user_query}'. No exact match found. Provide a calm, spa-themed response."

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a spa desk assistant providing wellness and service details in a soothing tone."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Sorry, I'm having trouble accessing the spa service right now. (Error: {str(e)})"
