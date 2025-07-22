import pandas as pd
import json
from datetime import datetime
from agents.email_sender import send_confirmation_email

availability_df = pd.read_csv("data/room_availability.csv")

def book_room(guest, room_type, checkin, checkout):
    record = {
        "type": "Room",
        "room_type": room_type,
        "checkin": checkin,
        "checkout": checkout,
        "guest": guest,
        "timestamp": datetime.now().isoformat()
    }
    with open("data/bookings.json", "a") as f:
        f.write(json.dumps(record) + "\n")

    body = f"""Hello {guest['first_name']} {guest['last_name']},

Your room booking is confirmed.

Room Type: {room_type}
Check-in: {checkin}
Check-out: {checkout}

We look forward to your stay!

— Hotel Team
"""
    send_confirmation_email(guest['email'], "Room Booking Confirmation", body)