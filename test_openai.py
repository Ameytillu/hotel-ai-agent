from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
    messages=[{"role": "user", "content": "Say hello from my hotel AI agent!"}]
)

print(response.choices[0].message.content)
