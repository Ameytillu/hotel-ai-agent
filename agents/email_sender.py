import smtplib
from email.message import EmailMessage

def send_confirmation_email(to_email, subject, body_text):
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = "hotel@yourdomain.com"
    message["To"] = to_email
    message.set_content(body_text)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("your-email", "your-password")
        server.send_message(message)