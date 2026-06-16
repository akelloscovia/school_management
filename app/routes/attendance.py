from flask import Blueprint, request
from datetime import datetime, timedelta
from app import db
from app.models import Attendance, Student, AttendanceStatus, StudentParent
from app.utils.decorators import (
    token_required, teacher_or_admin_required, validate_request_json,
    get_pagination_params, paginate_query
)
from app.utils.helpers import ResponseFormatter

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('', methods=['POST'])
@token_required
@teacher_or_admin_required
@validate_request_json('student_id', 'date', 'status')
def record_attendance(current_user):
    """Record attendance for a student"""
    data = request.get_json()
    
    student = Student.query.get(data['student_id'])
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    try:
        attendance_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return ResponseFormatter.error('Invalid date format. Use YYYY-MM-DD', status_code=400)
    
    # Check if attendance already recorded for this date
    existing = Attendance.query.filter_by(
        student_id=data['student_id'],
        date=attendance_date
    ).first()
    
    if existing:
        existing.status = data['status']
        existing.remarks = data.get('remarks')
        existing.recorded_at = datetime.utcnow()
    else:
        existing = Attendance(
            student_id=data['student_id'],
            date=attendance_date,
            status=data['status'],
            remarks=data.get('remarks'),
            recorded_by_id=current_user.id
        )
        db.session.add(existing)
    
    try:
        db.session.commit()
        return ResponseFormatter.success(
            data=existing.to_dict(),
            message='Attendance recorded successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error recording attendance: {str(e)}', status_code=500)


@attendance_bp.route('/student/<int:student_id>', methods=['GET'])
@token_required
def get_student_attendance(current_user, student_id):
    """Get attendance records for a student"""
    page, per_page = get_pagination_params()
    
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    # Date range filter
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Attendance.query.filter_by(student_id=student_id)
    
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.date >= start)
        except ValueError:
            return ResponseFormatter.error('Invalid start_date format', status_code=400)
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.date <= end)
        except ValueError:
            return ResponseFormatter.error('Invalid end_date format', status_code=400)
    
    query = query.order_by(Attendance.date.desc())
    result = paginate_query(query, page, per_page)
    
    return ResponseFormatter.success(data=result)


@attendance_bp.route('/class/<int:class_id>/date/<date_str>', methods=['GET'])
@token_required
@teacher_or_admin_required
def get_class_attendance_by_date(current_user, class_id, date_str):
    """Get attendance records for a class on a specific date"""
    try:
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return ResponseFormatter.error('Invalid date format. Use YYYY-MM-DD', status_code=400)
    
    records = db.session.query(Attendance).join(Student).filter(
        Student.class_id == class_id,
        Attendance.date == attendance_date
    ).all()
    
    return ResponseFormatter.success(data=[r.to_dict() for r in records])


@attendance_bp.route('/class/<int:class_id>/date/<date_str>/absentees', methods=['GET'])
@token_required
@teacher_or_admin_required
def get_class_absentees(current_user, class_id, date_str):
    """Get absent students for a class on a specific date"""
    try:
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return ResponseFormatter.error('Invalid date format. Use YYYY-MM-DD', status_code=400)
    
    absent_records = db.session.query(Attendance).join(Student).filter(
        Student.class_id == class_id,
        Attendance.date == attendance_date,
        Attendance.status == AttendanceStatus.ABSENT
    ).all()
    
    absentees = [record.student.to_dict(include_user=True) for record in absent_records]
    return ResponseFormatter.success(data=absentees)


@attendance_bp.route('/class/<int:class_id>/date/<date_str>/notify-parents', methods=['POST'])
@token_required
@teacher_or_admin_required
def notify_absent_parents(current_user, class_id, date_str):
    """Notify parents of absent students by SMS"""
    try:
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return ResponseFormatter.error('Invalid date format. Use YYYY-MM-DD', status_code=400)
    
    absent_records = db.session.query(Attendance).join(Student).filter(
        Student.class_id == class_id,
        Attendance.date == attendance_date,
        Attendance.status == AttendanceStatus.ABSENT
    ).all()
    
    notifications = []
    for record in absent_records:
        student = record.student
        parents = StudentParent.query.filter_by(student_id=student.id).all()
        for parent in parents:
            if parent.phone:
                notifications.append({
                    'student_id': student.id,
                    'student_name': f'{student.user.first_name} {student.user.last_name}',
                    'parent_name': parent.parent_name,
                    'parent_phone': parent.phone,
                    'message': f"{student.user.first_name} was absent on {attendance_date.isoformat()}"
                })
    
    return ResponseFormatter.success(
        data={'notifications': notifications, 'count': len(notifications)},
        message='Parent notifications prepared successfully'
    )


@attendance_bp.route('/bulk', methods=['POST'])
@token_required
@teacher_or_admin_required
@validate_request_json('class_id', 'date', 'attendance_records')
def bulk_record_attendance(current_user):
    """Record attendance for multiple students at once"""
    data = request.get_json()
    
    try:
        attendance_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return ResponseFormatter.error('Invalid date format. Use YYYY-MM-DD', status_code=400)
    
    attendance_records = data['attendance_records']
    created_count = 0
    updated_count = 0
    errors = []
    
    try:
        for record in attendance_records:
            student_id = record.get('student_id')
            status = record.get('status')
            remarks = record.get('remarks', '')
            
            student = Student.query.get(student_id)
            if not student:
                errors.append(f"Student {student_id} not found")
                continue
            
            existing = Attendance.query.filter_by(
                student_id=student_id,
                date=attendance_date
            ).first()
            
            if existing:
                existing.status = status
                existing.remarks = remarks
                updated_count += 1
            else:
                attendance = Attendance(
                    student_id=student_id,
                    date=attendance_date,
                    status=status,
                    remarks=remarks,
                    recorded_by_id=current_user.id
                )
                db.session.add(attendance)
                created_count += 1
        
        db.session.commit()
        
        return ResponseFormatter.success(
            data={
                'created': created_count,
                'updated': updated_count,
                'errors': errors
            },
            message='Bulk attendance recorded successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error recording attendance: {str(e)}', status_code=500)


@attendance_bp.route('/summary/<int:student_id>', methods=['GET'])
@token_required
def get_attendance_summary(current_user, student_id):
    """Get attendance summary for a student"""
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    if not month or not year:
        today = datetime.now()
        month = today.month
        year = today.year
    
    records = Attendance.query.filter(
        Attendance.student_id == student_id,
        db.func.month(Attendance.date) == month,
        db.func.year(Attendance.date) == year
    ).all()
    
    total = len(records)
    present = sum(1 for r in records if r.status in [AttendanceStatus.PRESENT, AttendanceStatus.LATE])
    absent = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
    late = sum(1 for r in records if r.status == AttendanceStatus.LATE)
    excused = sum(1 for r in records if r.status == AttendanceStatus.EXCUSED)
    
    percentage = (present / total * 100) if total > 0 else 0
    
    return ResponseFormatter.success(data={
        'month': month,
        'year': year,
        'total_days': total,
        'present': present,
        'absent': absent,
        'late': late,
        'excused': excused,
        'percentage': round(percentage, 2)
    })


@attendance_bp.route('', methods=['GET'])
@token_required
def get_attendance_by_date(current_user):
    """Get attendance records for a specific date"""
    date_str = request.args.get('date')
    
    if not date_str:
        return ResponseFormatter.error('Date parameter is required', status_code=400)
    
    try:
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return ResponseFormatter.error('Invalid date format. Use YYYY-MM-DD', status_code=400)
    
    records = Attendance.query.filter_by(date=attendance_date).all()
    
    result = {
        'items': [r.to_dict() for r in records],
        'total': len(records),
        'date': date_str
    }
    
    return ResponseFormatter.success(data=result)
