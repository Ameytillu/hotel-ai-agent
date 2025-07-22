import pandas as pd
import json
from datetime import datetime
from agents.email_sender import send_confirmation_email

shuttle_df = pd.read_csv("data/shuttle_service.csv")

def book_shuttle(guest, pickup_time, from_location, to_location):
    record = {
        "type": "Shuttle",
        "pickup_time": pickup_time,
        "from": from_location,
        "to": to_location,
        "guest": guest,
        "timestamp": datetime.now().isoformat()
    }
    with open("data/bookings.json", "a") as f:
        f.write(json.dumps(record) + "\n")

    body = f"""Hello {guest['first_name']} {guest['last_name']},

Your shuttle service has been booked.

Pickup: {pickup_time}
From: {from_location}
To: {to_location}

Safe travels!

— Hotel Team
"""
    send_confirmation_email(guest['email'], "Shuttle Booking Confirmation", body)