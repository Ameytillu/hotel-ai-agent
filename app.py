import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import openai

# === Load environment variables ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

# === Import router agent ===
from agents.router_agent import route_query
from agents.rag_agent import search_rag_database

# === Streamlit Page Configuration ===
st.set_page_config(
    page_title="Hotel Concierge AI - Your Smart Assistant", 
    page_icon="🏨", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# === Custom CSS for modern UI ===
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* User message */
    [data-testid="stChatMessageContent"] {
        color: #1a1a2e;
    }
    
    /* Input box */
    .stChatInputContainer {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: rgba(255, 255, 255, 0.05);
    }
    
    /* Headers */
    h1 {
        color: white;
        font-weight: 700;
        text-align: center;
        padding: 1rem 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Info boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        border: none;
    }
    
    /* Make sidebar text white */
    [data-testid="stSidebar"] * {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# === Header with icon ===
st.markdown("""
<div style="text-align: center; padding: 2rem 0 1rem 0;">
    <div style="display: inline-block; background: rgba(255, 255, 255, 0.2); padding: 1.5rem; border-radius: 20px; backdrop-filter: blur(10px);">
        <h1 style="margin: 0; font-size: 3rem;">🏨 Hotel Concierge AI</h1>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; color: white; font-size: 1.2rem; padding: 0 2rem 2rem 2rem; max-width: 800px; margin: 0 auto;">
    <p style="background: rgba(255, 255, 255, 0.1); padding: 1.5rem; border-radius: 15px; backdrop-filter: blur(10px);">
        Your personalized <strong>AI Concierge</strong> — powered by <strong>OpenAI GPT-4o</strong> and your hotel's custom AI agents.<br>
        Ask me anything about <strong>bookings</strong>, <strong>restaurant menu</strong>, <strong>spa services</strong>, 
        <strong>policies</strong>, <strong>FAQs</strong>, or <strong>shuttle timings</strong> — I'll automatically route your question to the right department.
    </p>
</div>
""", unsafe_allow_html=True)

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

# === Sidebar ===
with st.sidebar:
    st.markdown("### 🧠 System Information")
    st.info(f"✅ OpenAI version: {openai.__version__}")
    
    st.markdown("---")
    
    st.markdown("### 💡 Features")
    st.markdown("""
    - **Unified Router Agent**
    - **Automatic Intent Detection**
    - **Multi-Agent System**
    - **RAG Knowledge Base**
    - **Voice & SMS Support**
    """)
    
    st.markdown("---")
    
    st.markdown("### 🎯 Available Services")
    services = [
        "🛏️ Room Bookings",
        "🍽️ Restaurant Reservations",
        "💆 Spa Appointments",
        "🚐 Shuttle Service",
        "📋 Hotel Policies",
        "❓ FAQs & General Info"
    ]
    for service in services:
        st.markdown(f"- {service}")
