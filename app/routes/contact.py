from flask import Blueprint, request
from app import db
from app.models import ContactInfo, ContactMessage
from app.utils.helpers import ResponseFormatter

contact_bp = Blueprint('contact', __name__)


@contact_bp.route('/contact_info', methods=['GET'])
def get_contact_info():
    contact_items = ContactInfo.query.order_by(ContactInfo.id).all()
    data = [item.to_dict() for item in contact_items]
    return ResponseFormatter.success(data=data)


@contact_bp.route('/contact_info', methods=['POST'])
def create_contact_info():
    data = request.get_json(silent=True) or {}
    try:
        contact_info = ContactInfo(
            email=data.get('email'),
            phone_number=data.get('phone_number'),
            address=data.get('address'),
            map_embed_url=data.get('map_embed_url')
        )
        db.session.add(contact_info)
        db.session.commit()

        return ResponseFormatter.success(data=contact_info.to_dict(), message='Contact info created', status_code=201)
    except Exception as exc:
        db.session.rollback()
        return ResponseFormatter.error(f'Unable to create contact info: {str(exc)}', status_code=500)


@contact_bp.route('/contact_info/<int:contact_id>', methods=['PUT'])
def update_contact_info(contact_id):
    contact_info = ContactInfo.query.get(contact_id)
    if not contact_info:
        return ResponseFormatter.error('Contact info not found', status_code=404)

    data = request.get_json(silent=True) or {}
    try:
        contact_info.email = data.get('email', contact_info.email)
        contact_info.phone_number = data.get('phone_number', contact_info.phone_number)
        contact_info.address = data.get('address', contact_info.address)
        contact_info.map_embed_url = data.get('map_embed_url', contact_info.map_embed_url)
        db.session.commit()

        return ResponseFormatter.success(data=contact_info.to_dict(), message='Contact info updated')
    except Exception as exc:
        db.session.rollback()
        return ResponseFormatter.error(f'Unable to update contact info: {str(exc)}', status_code=500)


@contact_bp.route('/contact_message', methods=['GET'])
def get_contact_messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return ResponseFormatter.success(data=[message.to_dict() for message in messages])


@contact_bp.route('/contact_message', methods=['POST'])
def create_contact_message():
    data = request.get_json(silent=True) or {}

    try:
        contact_message = ContactMessage(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            message=data.get('message'),
            reply=data.get('reply')
        )
        db.session.add(contact_message)
        db.session.commit()

        return ResponseFormatter.success(data=contact_message.to_dict(), message='Contact message created', status_code=201)
    except Exception as exc:
        db.session.rollback()
        return ResponseFormatter.error(f'Unable to create contact message: {str(exc)}', status_code=500)
