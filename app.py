import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import openai

# === Display current OpenAI version on sidebar ===
st.sidebar.info(f"✅ OpenAI version: {openai.__version__}")

# === Load environment variables ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

# === Import router agent ===
from agents.router_agent import route_query
from agents.rag_agent import search_rag_database

# === Streamlit Page Configuration ===
st.set_page_config(page_title="🏨 Hotel Concierge AI", page_icon="🏨", layout="centered")

st.title("🏨 Hotel Concierge AI")
st.markdown("""
Your personalized **AI Concierge** — powered by **OpenAI GPT-4o** and your hotel’s custom AI agents.  
Ask me anything related to **bookings**, **restaurant menu**, **spa services**, **policies**, **FAQs**, or **shuttle timings** —  
I’ll automatically route your question to the right department.
""")

# === Maintain chat history ===
if "history" not in st.session_state:
    st.session_state.history = []

# === Chat input field ===
user_query = st.chat_input("Type your message here...")

def get_router_response(message):
    """
    Handles RAG lookup + router agent decision automatically.
    """
    try:
        # Step 1 — Check RAG database first (local knowledge)
        rag_response = search_rag_database(message)
        if rag_response:
            return rag_response

        # Step 2 — Route query to appropriate agent
        response = route_query(message)
        return response

    except Exception as e:
        return f"⚠️ Error while processing your request: {str(e)}"

# === Display chat history ===
for chat in st.session_state.history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# === Handle new messages ===
if user_query:
    st.session_state.history.append({"role": "user", "content": user_query})

    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        reply = get_router_response(user_query)
        st.markdown(reply)

    st.session_state.history.append({"role": "assistant", "content": reply})

# === Footer ===
st.sidebar.markdown("""
---
🧠 **Mode:** Unified Router Agent  
💡 This system automatically selects the correct hotel agent for each query.
""")
