from flask import Blueprint, request, current_app
from app import db
from app.models import Student, User, Role
from app.models.website import AdmissionApplication
from app.utils.decorators import token_required, admin_required
from app.utils.helpers import ResponseFormatter, generate_admission_number
from datetime import datetime

admissions_bp = Blueprint('admissions', __name__)


@admissions_bp.route('/pending', methods=['GET'])
@token_required
@admin_required
def get_pending_admissions(current_user):
    """Get all pending admissions directly from database"""
    try:
        applications = AdmissionApplication.query.filter(
            AdmissionApplication.status.in_(['Pending', 'Approved'])
        ).order_by(AdmissionApplication.submitted_at.desc()).all()
        
        pending = [app.to_dict() for app in applications]
        
        return ResponseFormatter.success(data={'applications': pending})
    except Exception as e:
        current_app.logger.error(f"Error fetching admissions: {e}")
        return ResponseFormatter.error(f"Error fetching admissions: {str(e)}", status_code=500)


@admissions_bp.route('/approve/<int:app_id>', methods=['POST'])
@token_required
@admin_required
def approve_admission(current_user, app_id):
    """Approve an admission"""
    data = request.get_json() or {}
    
    try:
        application = AdmissionApplication.query.get(app_id)
        if not application:
            return ResponseFormatter.error("Application not found", status_code=404)
            
        application.status = 'Approved'
        if data.get('student_id'):
            application.mgnt_student_id = data.get('student_id')
            
        db.session.commit()
        
        return ResponseFormatter.success(
            data=application.to_dict(),
            message='Admission approved successfully',
            status_code=200
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error approving admission: {e}")
        return ResponseFormatter.error(f"Error approving admission: {str(e)}", status_code=500)


@admissions_bp.route('/reject/<int:app_id>', methods=['POST'])
@token_required
@admin_required
def reject_admission(current_user, app_id):
    """Reject an admission application"""
    data = request.get_json() or {}
    
    try:
        application = AdmissionApplication.query.get(app_id)
        if not application:
            return ResponseFormatter.error("Application not found", status_code=404)
            
        application.status = 'Rejected'
        application.rejection_reason = data.get('reason', 'Application was not approved')
        
        db.session.commit()
        
        return ResponseFormatter.success(
            data=application.to_dict(),
            message='Admission rejected successfully',
            status_code=200
        )
    except Exception as e:
        db.session.rollback()
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
    
    try:
        application = AdmissionApplication.query.get(data['app_id'])
        if not application:
            return ResponseFormatter.error("Admission application not found", status_code=404)
            
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
        
        # Sync back to admission application
        application.status = 'Enrolled'
        application.mgnt_student_id = student.id
        application.mgnt_admission_number = student.admission_number
        
        db.session.commit()
        
        return ResponseFormatter.success(
            data=student.to_dict(include_user=True),
            message='Student enrolled successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error enrolling student: {e}")
        return ResponseFormatter.error(f"Error enrolling student: {str(e)}", status_code=500)
