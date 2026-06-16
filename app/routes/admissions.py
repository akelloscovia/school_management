from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Student, User, Role, Class
from app.utils.decorators import token_required, admin_required
from app.utils.helpers import ResponseFormatter, generate_admission_number
from datetime import datetime
import requests
import json

admissions_bp = Blueprint('admissions', __name__, url_prefix='/api/admissions')


@admissions_bp.route('/pending', methods=['GET'])
@token_required
@admin_required
def get_pending_admissions(current_user):
    """Get all pending admissions from website backend"""
    website_backend_url = current_app.config.get(
        'WEBSITE_BACKEND_URL', 
        'http://localhost:5001'
    )
    
    try:
        # Get applications from website backend
        response = requests.get(
            f"{website_backend_url}/api/v1/admissions/applications",
            headers={'Authorization': request.headers.get('Authorization', '')},
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        applications = data if isinstance(data, list) else data.get('applications', [])
        
        # Filter for pending and approved only
        pending = [app for app in applications if app.get('status') in ['Pending', 'Approved']]
        
        return ResponseFormatter.success(data={'applications': pending})
    except Exception as e:
        current_app.logger.error(f"Error fetching admissions from website: {e}")
        return ResponseFormatter.error(f"Error fetching admissions: {str(e)}", status_code=500)


@admissions_bp.route('/approve/<int:app_id>', methods=['POST'])
@token_required
@admin_required
def approve_admission(current_user, app_id):
    """Approve an admission and create student in SMS, then sync back to website"""
    data = request.get_json() or {}
    website_backend_url = current_app.config.get(
        'WEBSITE_BACKEND_URL', 
        'http://localhost:5001'
    )
    
    try:
        # First, notify website backend of approval
        approval_data = {
            'mgnt_student_id': data.get('student_id'),
            'approved_by': current_user.id
        }
        
        response = requests.put(
            f"{website_backend_url}/api/v1/admissions/applications/{app_id}/approve",
            json=approval_data,
            headers={'Authorization': request.headers.get('Authorization', '')},
            timeout=10
        )
        response.raise_for_status()
        
        return ResponseFormatter.success(
            data=response.json(),
            message='Admission approved successfully',
            status_code=200
        )
    except Exception as e:
        current_app.logger.error(f"Error approving admission: {e}")
        return ResponseFormatter.error(f"Error approving admission: {str(e)}", status_code=500)


@admissions_bp.route('/reject/<int:app_id>', methods=['POST'])
@token_required
@admin_required
def reject_admission(current_user, app_id):
    """Reject an admission application"""
    data = request.get_json() or {}
    website_backend_url = current_app.config.get(
        'WEBSITE_BACKEND_URL', 
        'http://localhost:5001'
    )
    
    try:
        rejection_data = {
            'reason': data.get('reason', 'Application was not approved')
        }
        
        response = requests.put(
            f"{website_backend_url}/api/v1/admissions/applications/{app_id}/reject",
            json=rejection_data,
            headers={'Authorization': request.headers.get('Authorization', '')},
            timeout=10
        )
        response.raise_for_status()
        
        return ResponseFormatter.success(
            data=response.json(),
            message='Admission rejected successfully',
            status_code=200
        )
    except Exception as e:
        current_app.logger.error(f"Error rejecting admission: {e}")
        return ResponseFormatter.error(f"Error rejecting admission: {str(e)}", status_code=500)


@admissions_bp.route('/enroll', methods=['POST'])
@token_required
@admin_required
def enroll_student(current_user):
    """Create a student record from an approved admission"""
    data = request.get_json() or {}
    required = ['student_name', 'parent_email', 'date_of_birth', 'gender', 'class_id', 'app_id']
    
    missing = [f for f in required if not data.get(f)]
    if missing:
        return ResponseFormatter.error(f'Missing fields: {", ".join(missing)}', status_code=400)
    
    website_backend_url = current_app.config.get(
        'WEBSITE_BACKEND_URL', 
        'http://localhost:5001'
    )
    
    try:
        # Parse student name
        name_parts = data['student_name'].strip().split()
        first_name = name_parts[0] if name_parts else 'Student'
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else 'Applicant'
        
        # Create email
        safe_first = ''.join(c for c in first_name.lower() if c.isalnum()) or 'student'
        safe_last = ''.join(c for c in last_name.lower() if c.isalnum()) or 'applicant'
        student_email = f"{safe_first}.{safe_last}@hilltop.local"
        
        # Create user account
        student_role = Role.query.filter_by(name='student').first()
        if not student_role:
            return ResponseFormatter.error('Student role not configured', status_code=500)
        
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=student_email,
            role_id=student_role.id
        )
        user.set_password(current_app.config.get('MGNT_DEFAULT_STUDENT_PASSWORD', 'Hilltop2026!'))
        db.session.add(user)
        db.session.flush()
        
        # Create student record
        student = Student(
            user_id=user.id,
            admission_number=generate_admission_number(),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
            gender=data['gender'],
            address=data.get('address', ''),
            medical_info=data.get('medical_info', ''),
            class_id=int(data['class_id']),
            admission_status='admitted'
        )
        db.session.add(student)
        db.session.commit()
        
        # Sync back to website backend
        sync_data = {
            'student_id': student.id,
            'student_name': data['student_name'],
            'parent_email': data['parent_email'],
            'admission_number': student.admission_number,
            'student_email': student_email
        }
        
        try:
            requests.post(
                f"{website_backend_url}/api/v1/admissions/webhook/sync-status",
                json=sync_data,
                timeout=10
            )
        except Exception as e:
            current_app.logger.warning(f"Failed to sync admission status to website: {e}")
        
        return ResponseFormatter.success(
            data=student.to_dict(include_user=True),
            message='Student enrolled successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error enrolling student: {e}")
        return ResponseFormatter.error(f"Error enrolling student: {str(e)}", status_code=500)
