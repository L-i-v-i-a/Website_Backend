from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from email.message import EmailMessage
import os
import smtplib
import ssl
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

contact_bp = Blueprint('contact', __name__)

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["Cluster0"]
contacts_collection = db["contacts"]

# Email settings
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


@contact_bp.route('/contact-us', methods=['POST'])
def contact():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    message = data.get('message')

    if not all([name, email, message]):
        return jsonify({"error": "Name, email, and message are required."}), 400

    try:
        # Save to MongoDB
        contact_entry = {
            "name": name,
            "email": email,
            "phone": phone,
            "message": message,
            "submitted_at": datetime.utcnow()
        }
        contacts_collection.insert_one(contact_entry)

        # Compose email
        subject = f"New Contact Form Submission from {name}"
        body = f"""\
Name: {name}
Email: {email}
Phone: {phone or 'N/A'}

Message:
{message}
"""
        send_email(subject, body)

        return jsonify({"message": "Message sent successfully."}), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": "Failed to process message."}), 500


def send_email(subject, body):
    try:
        msg = EmailMessage()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject
        msg.set_content(body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

    except Exception as e:
        print("❌ Email sending failed:", e)
        raise
