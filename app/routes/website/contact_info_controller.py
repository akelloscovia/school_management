from flask import Blueprint, request, jsonify
from app import db
from app.models.website import WebsiteContactInfo as Contact_Info  
from app.status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_201_CREATED,
    HTTP_200_OK, HTTP_404_NOT_FOUND
)

website_contact_info_bp = Blueprint("contact_info", __name__)
# CREATE: Add new contact info
@website_contact_info_bp.route("/", methods=["POST"])
def create_contact():
    data = request.get_json() or {}

    required_fields = ["address", "phone_number", "email"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), HTTP_400_BAD_REQUEST

    contact = Contact_Info(
        address=data["address"],
        phone_number=data["phone_number"],
        email=data["email"],
        map_embed_url=data.get("map_embed_url"),
        working_hours=data.get("working_hours"),
        additional_notes=data.get("additional_notes")
    )

    db.session.add(contact)
    db.session.commit()
    return jsonify({"message": "Contact info created successfully", "contact": {
        "id": contact.id,
        "address": contact.address,
        "phone_number": contact.phone_number,
        "email": contact.email,
        "map_embed_url": contact.map_embed_url,
        "working_hours": contact.working_hours,
        "additional_notes": contact.additional_notes
    }}), HTTP_201_CREATED


# READ: Get all contact info entries
@website_contact_info_bp.route("/", methods=["GET"], strict_slashes=False)
def get_all_contacts():
    contacts = Contact_Info.query.all()
    result = []
    for c in contacts:
        result.append({
            "id": c.id,
            "address": c.address,
            "phone_number": c.phone_number,
            "email": c.email,
            "map_embed_url": c.map_embed_url,
            "working_hours": c.working_hours,
            "additional_notes": c.additional_notes
        })
    return jsonify(result), HTTP_200_OK

# READ: Get single contact by ID
@website_contact_info_bp.route("/<int:id>", methods=["GET"], strict_slashes=False)
def get_contact(id):
    contact = Contact_Info.query.get_or_404(id)
    return jsonify({
        "id": contact.id,
        "address": contact.address,
        "phone_number": contact.phone_number,
        "email": contact.email,
        "map_embed_url": contact.map_embed_url,
        "working_hours": contact.working_hours,
        "additional_notes": contact.additional_notes
    }), HTTP_200_OK


# UPDATE: Update contact info

@website_contact_info_bp.route("/<int:id>", methods=["PUT"], strict_slashes=False)
def update_contact(id):
    contact = Contact_Info.query.get_or_404(id)
    data = request.get_json() or {}

    contact.address = data.get("address", contact.address)
    contact.phone_number = data.get("phone_number", contact.phone_number)
    contact.email = data.get("email", contact.email)
    contact.map_embed_url = data.get("map_embed_url", contact.map_embed_url)
    contact.working_hours = data.get("working_hours", contact.working_hours)
    contact.additional_notes = data.get("additional_notes", contact.additional_notes)

    db.session.commit()
    return jsonify({"message": "Contact info updated successfully"}), HTTP_200_OK


# DELETE: Remove contact info
@website_contact_info_bp.route("/<int:id>", methods=["DELETE"], strict_slashes=False)
def delete_contact(id):
    contact = Contact_Info.query.get_or_404(id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({"message": "Contact info deleted successfully"}), HTTP_200_OK
