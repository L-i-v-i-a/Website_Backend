from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from email.message import EmailMessage
import os
import smtplib
import ssl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

subscribe_bp = Blueprint('/subscribe', __name__)

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["Cluster0"]
subscriptions_collection = db["subscriptions"]

# Email credentials
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


@subscribe_bp.route('/subscribe-now', methods=['POST'])
def subscribe():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"error": "Email is required."}), 400

    try:
        # Save to MongoDB
        subscription = {
            "email": email,
            "subscribed_at": datetime.utcnow()
        }
        subscriptions_collection.insert_one(subscription)

        # Compose email notification
        subject = "New Subscriber"
        body = f"📬 A new user has subscribed with the email:\n\n{email}"

        send_email(subject, body)

        return jsonify({"message": "Subscribed successfully."}), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": "Failed to subscribe."}), 500


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
