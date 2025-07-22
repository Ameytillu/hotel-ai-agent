import pandas as pd
import json
from datetime import datetime
from agents.email_sender import send_confirmation_email

spa_df = pd.read_csv("data/spa.csv")

def book_spa(guest, service_type, date_time):
    record = {
        "type": "Spa",
        "service": service_type,
        "appointment": date_time,
        "guest": guest,
        "timestamp": datetime.now().isoformat()
    }
    with open("data/bookings.json", "a") as f:
        f.write(json.dumps(record) + "\n")

    body = f"""Hello {guest['first_name']} {guest['last_name']},

Your spa appointment is confirmed.

Service: {service_type}
Time: {date_time}

We look forward to pampering you!

— Hotel Team
"""
    send_confirmation_email(guest['email'], "Spa Appointment Confirmation", body)