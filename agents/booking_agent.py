import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# === Load data once ===
ROOM_DATA_PATH = "data/room_availability.csv"


def booking_agent(user_input):
    """
    Handles a multi-turn hotel room booking conversation with memory.
    Step 1: Ask guest name and email
    Step 2: Ask check-in / check-out
    Step 3: Show available rooms with prices
    Step 4: Confirm booking and send email
    """

    # Initialize session variables
    if "booking_stage" not in st.session_state:
        st.session_state.booking_stage = "ask_name"
        st.session_state.booking_info = {}

    # === STEP 1: Guest Name ===
    if st.session_state.booking_stage == "ask_name":
        st.session_state.booking_info["guest_name"] = user_input.strip()
        st.session_state.booking_stage = "ask_email"
        return "Got it, may I have your email address for the booking confirmation?"

    # === STEP 2: Email ===
    elif st.session_state.booking_stage == "ask_email":
        st.session_state.booking_info["guest_email"] = user_input.strip()
        st.session_state.booking_stage = "ask_checkin"
        return "Thanks! Could you please provide your check-in date (YYYY-MM-DD)?"

    # === STEP 3: Check-in ===
    elif st.session_state.booking_stage == "ask_checkin":
        st.session_state.booking_info["check_in"] = user_input.strip()
        st.session_state.booking_stage = "ask_checkout"
        return "Perfect. What’s your check-out date (YYYY-MM-DD)?"

    # === STEP 4: Check-out ===
    elif st.session_state.booking_stage == "ask_checkout":
        st.session_state.booking_info["check_out"] = user_input.strip()
        st.session_state.booking_stage = "show_rooms"

        # Load room data
        rooms_df = pd.read_csv(ROOM_DATA_PATH)
        available_rooms = rooms_df[rooms_df["available"] == True]

        # Build room summary
        room_summary = "\n".join(
            [f"- {row.room_type}: ${row.price}/night"
             for _, row in available_rooms.drop_duplicates("room_type").iterrows()]
        )

        return (
            f"Here are our available room types and rates:\n\n{room_summary}\n\n"
            "Please type the room type you'd like to reserve (e.g., 'Deluxe' or 'I want to book a suite')."
        )

    # === STEP 5: Room selection ===
    elif st.session_state.booking_stage == "show_rooms":
        room_choice = user_input.strip().lower()
        rooms_df = pd.read_csv(ROOM_DATA_PATH)

        # Try to find a room type mentioned in the user's text (more natural)
        match = None
        for rtype in rooms_df["room_type"].unique():
            if rtype.lower() in room_choice:
                match = rooms_df[rooms_df["room_type"].str.lower() == rtype.lower()]
                break

        if match is None or match.empty:
            return "Sorry, I didn’t recognize that room type. Please choose Standard, Deluxe, or Suite."

        selected_room = match.iloc[0]
        st.session_state.booking_info["room_type"] = selected_room.room_type
        st.session_state.booking_info["price"] = selected_room.price
        st.session_state.booking_stage = "confirm_booking"

        return (
            f"You’ve selected the {selected_room.room_type} room (${selected_room.price}/night). "
            "Would you like to confirm your booking? Please reply 'yes' or 'no'."
        )

    # === STEP 6: Confirmation ===
    elif st.session_state.booking_stage == "confirm_booking":
        user_reply = user_input.strip().lower()

        # Handle natural language confirmations
        if any(word in user_reply for word in ["yes", "confirm", "book", "sure", "go ahead"]):
            info = st.session_state.booking_info
            confirmation_msg = (
                f"🏨 **Booking Confirmation**\n\n"
                f"Guest: {info['guest_name']}\n"
                f"Room Type: {info['room_type']}\n"
                f"Check-in: {info['check_in']}\n"
                f"Check-out: {info['check_out']}\n"
                f"Rate: ${info['price']}/night\n\n"
                f"A confirmation email has been sent to {info['guest_email']}."
            )

            try:
                send_confirmation_email(info)
                st.session_state.active_agent = None
                st.session_state.booking_stage = None
                return confirmation_msg
            except Exception as e:
                st.session_state.active_agent = None
                st.session_state.booking_stage = None
                return f"⚠️ Error while processing your request: {str(e)}"

        elif any(word in user_reply for word in ["no", "cancel", "not now", "stop"]):
            st.session_state.active_agent = None
            st.session_state.booking_stage = None
            return "No problem! Your booking has been cancelled. Let me know if you’d like to try again later."

        else:
            return "I didn’t quite catch that. Please say 'yes' to confirm or 'no' to cancel."

    # === Reset fallback ===
    else:
        st.session_state.active_agent = None
        st.session_state.booking_stage = None
        return "Let's start fresh! Please say 'book a room' to begin again."


# === EMAIL FUNCTION ===
def send_confirmation_email(info):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = info["guest_email"]
    msg["Subject"] = f"Hotel Booking Confirmation - {info['guest_name']}"

    body = f"""
    Dear {info['guest_name']},

    Your booking has been confirmed successfully! 🎉

    Room Type: {info['room_type']}
    Check-in: {info['check_in']}
    Check-out: {info['check_out']}
    Rate: ${info['price']}/night

    Thank you for choosing our hotel.
    We look forward to hosting you soon!

    Best regards,
    Hotel Concierge AI
    """
    msg.attach(MIMEText(body, "plain"))

    # Gmail SMTP setup with App Password
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
