from datetime import datetime
from app import db


class ResponseFormatter:
    """Format API responses consistently"""
    
    @staticmethod
    def success(data=None, message='Success', status_code=200):
        """Format success response"""
        response = {
            'success': True,
            'message': message
        }
        if data is not None:
            response['data'] = data
        return response, status_code
    
    @staticmethod
    def error(message='Error', error_code=None, status_code=400):
        """Format error response"""
        response = {
            'success': False,
            'error': message
        }
        if error_code:
            response['error_code'] = error_code
        return response, status_code


def generate_admission_number():
    """Generate unique admission number"""
    from app.models import Student
    year = datetime.now().strftime('%Y')
    count = Student.query.filter_by().count() + 1
    return f"ADM{year}{count:04d}"


def calculate_attendance_percentage(student_id):
    """Calculate attendance percentage for a student"""
    from app.models import Attendance, AttendanceStatus
    
    total_records = Attendance.query.filter_by(student_id=student_id).count()
    
    if total_records == 0:
        return 0
    
    present_records = Attendance.query.filter(
        Attendance.student_id == student_id,
        Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE])
    ).count()
    
    return round((present_records / total_records) * 100, 2)


def calculate_average_marks(student_id, term=None, academic_year=None):
    """Calculate average marks for a student"""
    from app.models import Marks
    
    query = Marks.query.filter_by(student_id=student_id)
    
    if term:
        query = query.filter_by(term=term)
    if academic_year:
        query = query.filter_by(academic_year=academic_year)
    
    marks_records = query.all()
    
    if not marks_records:
        return 0
    
    total = sum(mark.percentage for mark in marks_records)
    return round(total / len(marks_records), 2)


def commit_to_db(obj=None):
    """Commit transaction to database"""
    try:
        db.session.add(obj) if obj else None
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Database error: {str(e)}")
        return False


def save_file(file, folder="hero"):
    from werkzeug.utils import secure_filename
    import os
    from flask import current_app
    if not file:
        return None
    filename = secure_filename(file.filename)
    
    upload_folder_base = current_app.config.get('UPLOAD_FOLDER_ABOUT', os.path.join(current_app.static_folder, 'uploads', 'about'))
    
    folder_map = {
        "hero": os.path.join(upload_folder_base, 'hero'),
        "operations": os.path.join(upload_folder_base, 'operations'),
        "team": os.path.join(upload_folder_base, 'team'),
        "pillars": os.path.join(upload_folder_base, 'pillars'),
        "focus_areas": os.path.join(upload_folder_base, 'focus_areas')
    }
    path = os.path.join(folder_map.get(folder, upload_folder_base), filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    file.save(path)
    return f"/api/v1/about/uploads/{folder}/{filename}"
