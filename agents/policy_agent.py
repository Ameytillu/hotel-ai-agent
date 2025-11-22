# agents/policy_agent.py

from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Load environment variables (OpenAI key)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

def policy_response(user_query: str):
    """
    Answers questions related to hotel policies using the local JSON file (hotel_policies.csv or JSON).
    Falls back to OpenAI API if no direct policy match is found.
    """
    # Try to load your local policy data (CSV or JSON)
    try:
        with open("data/hotel_policies.csv", "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    user_query_lower = user_query.lower()
    matched_line = None

    for line in lines:
        if user_query_lower in line.lower():
            matched_line = line.strip()
            break

    # If a local policy is found, use it directly
    if matched_line:
        prompt = f"A guest asked: '{user_query}'. Here is the relevant hotel policy: {matched_line}. Provide a friendly and clear answer."
    else:
        prompt = f"A guest asked about hotel policy: '{user_query}'. Provide a helpful and professional response based on general hospitality rules."

    # Generate answer using OpenAI API
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful hotel policy assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
    )

    return completion.choices[0].message.content.strip()
