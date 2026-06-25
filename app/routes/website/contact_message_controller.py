from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from flask_jwt_extended import jwt_required
from app.status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED,
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
)
from app import db
from app.models.website import WebsiteContactMessage as Contact_Message
import validators
import  requests

website_contact_message_bp = Blueprint("contact_message", __name__, url_prefix="/api/v1/contact_message")


# --- Helper function for Brevo ---
def send_brevo_email(to_email, to_name, subject, body):
    api_key = current_app.config.get("BREVO_API_KEY") or os.getenv("BREVO_API_KEY")
    sender_email = current_app.config.get("SENDER_EMAIL") or os.getenv("SENDER_EMAIL")
    sender_name = current_app.config.get("SENDER_NAME", "Hilltop Junior School")

    if not api_key:
        current_app.logger.warning('Brevo API key is not configured; skipping email send.')
        return {"error": "Brevo API key is not configured."}
    if not sender_email:
        current_app.logger.warning('Brevo sender email is not configured; skipping email send.')
        return {"error": "Brevo sender email is not configured."}

    url = "https://api.brevo.com/v3/smtp/email"
    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email,
        },
        "to": [{"email": to_email, "name": to_name}],
        "subject": subject,
        "textContent": body,
    }
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        response_text = getattr(e.response, 'text', str(e))
        status_code = getattr(e.response, 'status_code', 'N/A')
        current_app.logger.error(f"Brevo email send failed: {status_code} {response_text}")
        return {"error": "Brevo email send failed.", "details": response_text}


def notify_mgnt_contact_message(payload):
    mgnt_url = current_app.config.get('MGNT_API_URL', 'http://localhost:5000')
    webhook_secret = current_app.config.get('MGNT_WEBHOOK_SECRET', '')
    if not webhook_secret:
        current_app.logger.warning('MGNT webhook secret not configured; skipping contact message notification')
        return None

    endpoint = f"{mgnt_url.rstrip('/')}/api/communication/webhooks/contact-message"
    headers = {
        'Content-Type': 'application/json',
        'X-WEBHOOK-SECRET': webhook_secret
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        current_app.logger.warning(f"MGNT contact message notification failed: {e}")
        return None


# --- Submit a contact message ---
@website_contact_message_bp.route("", methods=["POST"])
def submit_contact():
    data = request.get_json(silent=True) or {}

    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    message = (data.get("message") or "").strip()

    if not first_name or not last_name or not message:
        return jsonify({"error": "first_name, last_name, and message are required."}), HTTP_400_BAD_REQUEST

    if email and not validators.email(email):
        return jsonify({"error": "Invalid email format."}), HTTP_400_BAD_REQUEST

    try:
        contact_msg = Contact_Message(
            first_name=first_name,
            last_name=last_name,
            email=email if email else None,
            phone=phone if phone else None,
            message=message,
        )
        db.session.add(contact_msg)
        db.session.commit()

        notify_mgnt_contact_message({
            'subject': f'Website contact message from {first_name} {last_name}',
            'body': (
                f"New message from {first_name} {last_name} "
                f"({email or 'no email provided'}, {phone or 'no phone provided'}):\n\n{message}"
            ),
            'contact_email': email,
            'contact_phone': phone,
            'first_name': first_name,
            'last_name': last_name,
            'message': message,
        })

        return jsonify({"message": "Message sent successfully."}), HTTP_201_CREATED
    except Exception:
        current_app.logger.exception("Failed to save contact message")
        db.session.rollback()
        return jsonify({"error": "Failed to submit message."}), HTTP_500_INTERNAL_SERVER_ERROR


# --- Get all messages ---
@website_contact_message_bp.route("", methods=["GET"])
def get_messages():
    try:
        messages = Contact_Message.query.order_by(Contact_Message.created_at.desc()).all()
        result = []
        for msg in messages:
            result.append({
                "id": msg.id,
                "first_name": msg.first_name,
                "last_name": msg.last_name,
                "email": msg.email,
                "phone": msg.phone,
                "message": msg.message,
                "reply": msg.reply,
                "created_at": msg.created_at.isoformat(),
            })
        return jsonify(result), HTTP_200_OK
    except Exception:
        current_app.logger.exception("Failed to fetch contact messages")
        return jsonify({"error": "Failed to load contact messages"}), HTTP_500_INTERNAL_SERVER_ERROR


# --- Reply to a message (and send email) ---
@website_contact_message_bp.route("/<int:id>/reply", methods=["PUT"])
def update_reply(id):
    data = request.get_json()
    reply = (data.get("reply") or "").strip()

    if not reply:
        return jsonify({"error": "Reply text is required"}), HTTP_400_BAD_REQUEST

    contact_msg = Contact_Message.query.get(id)
    if not contact_msg:
        return jsonify({"error": "Message not found"}), HTTP_404_NOT_FOUND

    try:
        contact_msg.reply = reply
        contact_msg.replied_at = datetime.now()
        db.session.commit()

        # Send reply email if user provided one
        if contact_msg.email:
            try:
                result = send_brevo_email(
                    to_email=contact_msg.email,
                    to_name=contact_msg.first_name,
                    subject="Reply to your message",
                    body=f"Hi {contact_msg.first_name},\n\n"
                         f"Thanks for contacting us. Here's our reply:\n\n"
                         f"{reply}\n\n"
                         f"Best regards,\nhilltop junior school"
                )
                current_app.logger.info(f"Brevo send result: {result}")
            except Exception as e:
                current_app.logger.error(f"Email send failed: {e}")

        return jsonify({"message": "Reply updated and email sent"}), HTTP_200_OK

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed to update reply")
        return jsonify({"error": "Failed to update reply"}), HTTP_500_INTERNAL_SERVER_ERROR


# --- Delete reply only ---
@website_contact_message_bp.route("/<int:id>/reply", methods=["DELETE"])
def delete_reply(id):
    contact_msg = Contact_Message.query.get(id)
    if not contact_msg:
        return jsonify({"error": "Message not found"}), HTTP_404_NOT_FOUND

    contact_msg.reply = None
    db.session.commit()
    return jsonify({"message": "Reply deleted"}), HTTP_200_OK


# --- Delete entire message ---
@website_contact_message_bp.route("/<int:id>", methods=["DELETE"])
def delete_message(id):
    contact_msg = Contact_Message.query.get(id)
    if not contact_msg:
        return jsonify({"error": "Message not found"}), HTTP_404_NOT_FOUND

    db.session.delete(contact_msg)
    db.session.commit()
    return jsonify({"message": "Message deleted"}), HTTP_200_OK
