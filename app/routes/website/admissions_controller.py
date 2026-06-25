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
import secrets

# Blueprint definition
website_admissions_bp = Blueprint(
    'admissions',
      __name__, 
      url_prefix='/api/v1/admissions'

)

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


def parse_student_name(full_name):
    parts = [part.strip() for part in full_name.split() if part.strip()]
    if not parts:
        return 'Student', 'Applicant'
    if len(parts) == 1:
        return parts[0], 'Applicant'
    return parts[0], ' '.join(parts[1:])


def resolve_mgnt_class_id(grade_applied):
    mapping = current_app.config.get('MGNT_DEFAULT_CLASS_MAPPING', {
        'Daycare': 1,
        'Kindergarten': 2,
        'Primary 1': 3,
        'Primary 2': 4,
        'Primary 3': 5
    })
    if isinstance(mapping, str):
        try:
            mapping = json.loads(mapping)
        except Exception:
            mapping = {}
    return mapping.get(grade_applied) or current_app.config.get('MGNT_DEFAULT_CLASS_ID', 1)


def build_mgnt_student_payload(data):
    first_name, last_name = parse_student_name(data.get('student_name', 'Student Applicant'))
    safe_first = ''.join(c for c in first_name.lower() if c.isalnum()) or 'student'
    safe_last = ''.join(c for c in last_name.lower() if c.isalnum()) or 'applicant'
    email_domain = current_app.config.get('MGNT_DEFAULT_STUDENT_EMAIL_DOMAIN', 'hilltop.local')
    student_email = data.get('student_email')
    if not student_email:
        student_email = f"{safe_first}.{safe_last}@{email_domain}"

    return {
        'first_name': first_name,
        'last_name': last_name,
        'email': student_email,
        'password': current_app.config.get('MGNT_DEFAULT_STUDENT_PASSWORD', 'Hilltop2026!'),
        'date_of_birth': data.get('date_of_birth'),
        'gender': data.get('gender', 'Other'),
        'class_id': resolve_mgnt_class_id(data.get('grade_applied')),
        'address': data.get('address', ''),
        'medical_info': data.get('medical_info', ''),
        'photo_url': data.get('photo_url', ''),
        'admission_status': 'pending'
    }



# GET /api/v1/admissions/ - Admissions page info
@website_admissions_bp.route("/", methods=["GET"], strict_slashes=False)
def admissions_page():
    return jsonify(load_admissions_content()), 200


# UPDATE /api/v1/admissions/ - Admissions page save
@website_admissions_bp.route("/", methods=["PUT"], strict_slashes=False)
def update_admissions_page():
    data = {}
    if request.content_type and request.content_type.startswith('application/json'):
        data = request.get_json(silent=True) or {}
    else:
        # support FormData uploads from the React dashboard
        # JSON payload fields may be sent as strings
        data = request.form.to_dict(flat=True)

    content = load_admissions_content()

    def parse_list_field(value):
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                decoded = json.loads(value)
                if isinstance(decoded, list):
                    return decoded
            except Exception:
                pass
            return [line.strip() for line in value.splitlines() if line.strip()]
        if value is None:
            return []
        return [str(value)]

    def parse_dict_field(value):
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                decoded = json.loads(value)
                if isinstance(decoded, dict):
                    return decoded
            except Exception:
                pass
        return None

    if 'title' in data:
        content['title'] = data.get('title')
    if 'subtitle' in data:
        content['subtitle'] = data.get('subtitle')
    if 'description' in data:
        content['description'] = data.get('description')
    if 'requirements' in data:
        content['requirements'] = parse_list_field(data.get('requirements'))
    if 'steps' in data:
        content['steps'] = parse_list_field(data.get('steps'))
    if 'fees' in data:
        fees = parse_dict_field(data.get('fees'))
        if fees is not None:
            content['fees'] = fees
    if 'apply_button_text' in data:
        content['apply_button_text'] = data.get('apply_button_text')

    image_file = request.files.get('image')
    if image_file and image_file.filename:
        filename = secure_filename(image_file.filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        path = os.path.join(upload_folder, filename)
        image_file.save(path)
        content['image'] = f"uploads/products/{filename}"

    save_admissions_content(content)
    return jsonify(content), 200

# POST /api/v1/admissions/apply - Submit application
def parse_date(value):
    if isinstance(value, datetime.date):
        return value
    if not isinstance(value, str):
        raise ValueError('Invalid date value')

    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d'):
        try:
            return datetime.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError('Date must be in YYYY-MM-DD or DD/MM/YYYY format')


@website_admissions_bp.route("/apply", methods=["POST"])
def apply():
    data = request.get_json(silent=True) or request.form.to_dict(flat=True) or {}

    required_fields = ['student_name', 'date_of_birth', 'parent_name', 'parent_email', 'grade_applied', 'contact_number']
    missing_fields = [f for f in required_fields if not data.get(f)]
    if missing_fields:
        return jsonify({'error': f'Missing fields: {", ".join(missing_fields)}'}), 400

    try:
        dob_value = parse_date(data['date_of_birth'])

        new_app = AdmissionApplication(
            student_name=data['student_name'],
            date_of_birth=dob_value,
            parent_name=data['parent_name'],
            parent_email=data['parent_email'],
            grade_applied=data['grade_applied'],
            contact_number=data['contact_number'],
            submitted_at=datetime.datetime.utcnow(),
            status='Pending'
        )
        db.session.add(new_app)
        db.session.commit()
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to save application: {e}")
        return jsonify({'error': 'Failed to submit application'}), 500


    # Notify admin via email
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@hilltopjunior.ug')
    subject = f"New Admission Application: {new_app.student_name}"
    html_content = f"""
    <p>A new student admission application has been submitted.</p>
    <ul>
      <li>Student Name: {new_app.student_name}</li>
      <li>Date of Birth: {new_app.date_of_birth}</li>
      <li>Parent Name: {new_app.parent_name}</li>
      <li>Parent Email: {new_app.parent_email}</li>
      <li>Grade Applied: {new_app.grade_applied}</li>
      <li>Contact Number: {new_app.contact_number}</li>
      <li>Submitted At: {new_app.submitted_at}</li>
    </ul>
    """
    try:
        send_email(admin_email, subject, html_content)
    except Exception as e:
        current_app.logger.error(f"Failed to send admin email: {e}")

    return jsonify(new_app.to_dict()), 201

# GET /api/v1/admissions/applications - Admin view (JWT protected)
@website_admissions_bp.route("/applications", methods=["GET"])
@jwt_required()
def get_applications():
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role not in ["admin", "super_admin"]:
        return jsonify({"error": "Access denied"}), 403

    apps = AdmissionApplication.query.order_by(AdmissionApplication.submitted_at.desc()).all()
    return jsonify([a.to_dict() for a in apps]), 200

# GET /api/v1/admissions/applications/<id> - Get single application
@website_admissions_bp.route("/applications/<int:app_id>", methods=["GET"])
@jwt_required()
def get_application(app_id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role not in ["admin", "super_admin"]:
        return jsonify({"error": "Access denied"}), 403

    application = AdmissionApplication.query.get_or_404(app_id)
    return jsonify(application.to_dict()), 200


# GET /api/v1/admissions/track/<parent_email> - Parent tracking application status
@website_admissions_bp.route("/track/<parent_email>", methods=["GET"])
def track_application(parent_email):
    """Parents can track their application status using their email"""
    applications = AdmissionApplication.query.filter_by(parent_email=parent_email).all()
    if not applications:
        return jsonify({"error": "No applications found", "applications": []}), 404
    
    return jsonify({
        "parent_email": parent_email,
        "applications": [app.to_dict() for app in applications]
    }), 200


# PUT /api/v1/admissions/applications/<id>/approve - Approve application
@website_admissions_bp.route("/applications/<int:app_id>/approve", methods=["PUT"])
@jwt_required()
def approve_application(app_id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role not in ["admin", "super_admin"]:
        return jsonify({"error": "Access denied"}), 403

    application = AdmissionApplication.query.get_or_404(app_id)
    data = request.get_json() or {}
    
    try:
        application.status = 'Approved'
        application.mgnt_student_id = data.get('mgnt_student_id')
        db.session.commit()
        
        # Send approval email to parent
        subject = f"Admission Approved - {application.student_name}"
        html_content = f"""
        <h2>Congratulations!</h2>
        <p>Dear {application.parent_name},</p>
        <p>We are pleased to inform you that your child, {application.student_name}, has been approved for admission to our school.</p>
        <p><strong>Grade:</strong> {application.grade_applied}</p>
        <p>You can now access your student's portal using the credentials provided.</p>
        <p>Best regards,<br/>Hilltop Junior School</p>
        """
        try:
            send_email(application.parent_email, subject, html_content)
        except Exception as e:
            current_app.logger.error(f"Failed to send approval email: {e}")
        
        return jsonify(application.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# PUT /api/v1/admissions/applications/<id>/reject - Reject application
@website_admissions_bp.route("/applications/<int:app_id>/reject", methods=["PUT"])
@jwt_required()
def reject_application(app_id):
    current_user = User.query.get(get_jwt_identity())
    if not current_user or current_user.role not in ["admin", "super_admin"]:
        return jsonify({"error": "Access denied"}), 403

    application = AdmissionApplication.query.get_or_404(app_id)
    data = request.get_json() or {}
    
    try:
        application.status = 'Rejected'
        application.rejection_reason = data.get('reason', '')
        db.session.commit()
        
        # Send rejection email to parent
        subject = f"Admission Status Update - {application.student_name}"
        rejection_msg = data.get('reason', 'We regret to inform you that your application was not successful at this time.')
        html_content = f"""
        <h2>Application Status</h2>
        <p>Dear {application.parent_name},</p>
        <p>{rejection_msg}</p>
        <p>Please feel free to contact us if you would like to discuss this decision or reapply in the future.</p>
        <p>Best regards,<br/>Hilltop Junior School</p>
        """
        try:
            send_email(application.parent_email, subject, html_content)
        except Exception as e:
            current_app.logger.error(f"Failed to send rejection email: {e}")
        
        return jsonify(application.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# POST /api/v1/admissions/webhook/sync-status - MGNT sends status updates
@website_admissions_bp.route("/webhook/sync-status", methods=["POST"])
def sync_admission_status():
    """Receives status updates from MGNT system when student is created"""
    data = request.get_json() or {}
    
    try:
        # Find application by parent email and student name
        application = AdmissionApplication.query.filter_by(
            parent_email=data.get('parent_email'),
            student_name=data.get('student_name')
        ).first()
        
        if not application:
            return jsonify({"error": "Application not found"}), 404
        
        # Update with MGNT info
        application.status = 'Enrolled'
        application.mgnt_student_id = data.get('student_id')
        application.mgnt_admission_number = data.get('admission_number')
        db.session.commit()
        
        return jsonify({"message": "Status updated", "application": application.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to sync admission status: {e}")
        return jsonify({"error": str(e)}), 500
