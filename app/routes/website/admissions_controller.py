# app/controllers/admissions_controller.py

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models.website import AdmissionApplication
from app.models import User
from app.email_service import send_email
import datetime
import json
import os

# ✅ FIXED: unique blueprint name (THIS WAS YOUR MAIN BUG)
website_admissions_bp = Blueprint(
    'website_admissions',   # ✔ CHANGED FROM 'admissions'
    __name__)

DEFAULT_ADMISSIONS_CONTENT = {
    'title': 'Admissions',
    'subtitle': 'Welcome to Hilltop Junior School',
    'description': 'Join our vibrant learning community. We welcome students of all backgrounds.',
    'requirements': [
        'Daycare: 2-3 years',
        'Kindergarten: 4-5 years',
        'Primary: 6+ years',
        'Birth certificate',
        'Medical records',
        'Previous school records (if applicable)',
        'Parent identification'
    ],
    'steps': [
        'Complete the application form',
        'Submit required documents',
        'Schedule an interview',
        'Receive admission decision'
    ],
    'fees': {
        'items': [
            {'type': 'Daycare', 'amount': 'UGX 2,000,000/term'},
            {'type': 'Kindergarten', 'amount': 'UGX 2,500,000/term'},
            {'type': 'Primary', 'amount': 'UGX 3,000,000/term'}
        ],
        'registration': 'UGX 500,000 (one-time)'
    },
    'apply_button_text': 'Apply Now',
    'image': ''
}

CONTENT_FILE_NAME = 'admissions_page.json'


def get_content_file_path():
    instance_path = current_app.instance_path
    os.makedirs(instance_path, exist_ok=True)
    return os.path.join(instance_path, CONTENT_FILE_NAME)


def load_admissions_content():
    content_file = get_content_file_path()
    if os.path.exists(content_file):
        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_ADMISSIONS_CONTENT.copy()


def save_admissions_content(content):
    content_file = get_content_file_path()
    with open(content_file, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)


# GET admissions page
@website_admissions_bp.route("/", methods=["GET"], strict_slashes=False)
def admissions_page():
    return jsonify(load_admissions_content()), 200


# UPDATE admissions page
@website_admissions_bp.route("/", methods=["PUT"], strict_slashes=False)
def update_admissions_page():
    data = request.get_json(silent=True) or request.form.to_dict(flat=True)

    content = load_admissions_content()

    if 'title' in data:
        content['title'] = data.get('title')
    if 'subtitle' in data:
        content['subtitle'] = data.get('subtitle')
    if 'description' in data:
        content['description'] = data.get('description')
    if 'requirements' in data:
        content['requirements'] = data.get('requirements')
    if 'steps' in data:
        content['steps'] = data.get('steps')
    if 'fees' in data:
        try:
            content['fees'] = json.loads(data.get('fees'))
        except Exception:
            pass

    image_file = request.files.get('image')
    if image_file and image_file.filename:
        filename = secure_filename(image_file.filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        path = os.path.join(upload_folder, filename)
        image_file.save(path)
        content['image'] = f"uploads/{filename}"

    save_admissions_content(content)
    return jsonify(content), 200


# APPLY
@website_admissions_bp.route("/apply", methods=["POST"])
def apply():
    from app.models import User, Role, Message
    data = request.get_json(silent=True) or request.form.to_dict(flat=True)

    required = ['student_name', 'date_of_birth', 'parent_name', 'parent_email', 'grade_applied', 'contact_number']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        dob = datetime.datetime.strptime(data['date_of_birth'], "%Y-%m-%d").date()

        new_app = AdmissionApplication(
            student_name=data['student_name'],
            date_of_birth=dob,
            parent_name=data['parent_name'],
            parent_email=data['parent_email'],
            grade_applied=data['grade_applied'],
            contact_number=data['contact_number'],
            submitted_at=datetime.datetime.utcnow(),
            status='Pending'
        )

        db.session.add(new_app)
        db.session.flush()

        # Create or find Parent user
        parent_role = Role.query.filter_by(name='parent').first()
        parent_user = User.query.filter(db.func.lower(User.email) == data['parent_email'].lower().strip()).first()
        if not parent_user and parent_role:
            name_parts = data['parent_name'].strip().split()
            p_first = name_parts[0] if name_parts else 'Parent'
            p_last = ' '.join(name_parts[1:]) if len(name_parts) > 1 else 'User'
            parent_user = User(
                first_name=p_first,
                last_name=p_last,
                email=data['parent_email'].lower().strip(),
                phone=data['contact_number'],
                role_id=parent_role.id
            )
            parent_user.set_password('ilovehilltop')
            db.session.add(parent_user)
            db.session.flush()

        # Find first admin
        admin_role = Role.query.filter_by(name='admin').first()
        admin_user = User.query.filter_by(role_id=admin_role.id).first() if admin_role else None
        
        if parent_user and admin_user:
            # Create Message in the system inbox
            msg = Message(
                sender_id=parent_user.id,
                recipient_id=admin_user.id,
                subject=f"New Admission Application: {data['student_name']}",
                body=(
                    f"A new admission application has been submitted for {data['student_name']} (Grade: {data['grade_applied']}).\n"
                    f"Parent: {data['parent_name']}\n"
                    f"Contact: {data['contact_number']}\n"
                    f"Email: {data['parent_email']}"
                )
            )
            db.session.add(msg)

        db.session.commit()
        return jsonify(new_app.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# GET applications (admin)
@website_admissions_bp.route("/applications", methods=["GET"])
@jwt_required()
def get_applications():
    user = User.query.get(get_jwt_identity())
    if not user or user.role not in ["admin", "super_admin"]:
        return jsonify({"error": "Access denied"}), 403

    apps = AdmissionApplication.query.order_by(AdmissionApplication.submitted_at.desc()).all()
    return jsonify([a.to_dict() for a in apps]), 200