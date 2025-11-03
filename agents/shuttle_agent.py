from openai import OpenAI
from dotenv import load_dotenv
import os, pandas as pd

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

def shuttle_response(user_query: str):
    """Provides shuttle timing and route info from shuttle_service.csv."""
    try:
        df = pd.read_csv("data/shuttle_service.csv")
    except FileNotFoundError:
        df = pd.DataFrame()

    match = df[df['route'].str.contains(user_query, case=False, na=False)] if 'route' in df else None

    if match is not None and not match.empty:
        row = match.iloc[0]
        info = f"{row['service_name']} at {row['time']} – {row['route']} (${row['price']})"
        prompt = f"Guest asked: {user_query}\nSchedule found: {info}\nRespond clearly and helpfully."
    else:
        prompt = f"The guest asked: '{user_query}'. No exact shuttle match found. Provide a general shuttle service answer."

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a transportation assistant helping hotel guests with shuttle timings and routes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Sorry, I'm having trouble accessing shuttle information right now. (Error: {str(e)})"
