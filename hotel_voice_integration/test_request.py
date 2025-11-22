import openai
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Fixed text or get from RAG/chatbot
text = "Welcome to our hotel! How may I assist you?"

# Generate speech
response = openai.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=text
)

# Save audio file
with open("response.mp3", "wb") as f:
    f.write(response.content)

print("✅ Audio response saved as response.mp3")
