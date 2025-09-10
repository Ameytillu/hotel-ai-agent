# app.py

import streamlit as st
from model_loader import load_phi_model
import torch

# --- Page Settings ---
st.set_page_config(page_title="Phi SLM Fine-Tuned Hotel Agent", layout="wide")

# --- Load Fine-Tuned Model ---
@st.cache_resource(show_spinner="Loading Phi SLM Fine-Tuned model...")
def load_model():
    return load_phi_model("D:/your_model_directory")  # Update path if needed

tokenizer, model = load_model()

# --- UI Header ---
st.title("🏨 Hotel Concierge AI - Powered by Phi SLM (Fine-Tuned)")
st.markdown(
    """
    👋 Welcome to your personal **Hotel Concierge Agent**, powered by your **fine-tuned Phi LLM**!  
    This assistant understands **bookings, policies, FAQs, spa, shuttle, restaurant services**, and more.
    """
)

# --- Initialize Chat Memory ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Input Box for User ---
user_input = st.chat_input("Type a message like: 'I want to book a room from Friday to Sunday'")
if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate Response
    input_ids = tokenizer.encode(user_input, return_tensors="pt").to(model.device)
    output = model.generate(input_ids, max_new_tokens=250, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(output[0], skip_special_tokens=True)

    # Extract only assistant's reply
    reply = response.split(user_input)[-1].strip()

    st.chat_message("assistant").markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
