from flask import Blueprint, request
from datetime import datetime
from app import db
from app.models import TermReport, Marks, Student, Class, Attendance
from app.models.user import User, Role
from app.models.attendance import AttendanceStatus
from app.utils.decorators import (
    token_required, teacher_or_admin_required,
    get_pagination_params, paginate_query
)
from app.utils.helpers import ResponseFormatter

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/generate-term-report', methods=['POST'])
@token_required
@teacher_or_admin_required
def generate_term_report():
    """Generate term report for a student"""
    data = request.get_json()
    
    required_fields = ['student_id', 'term', 'academic_year']
    if not all(field in data for field in required_fields):
        return ResponseFormatter.error(f'Missing required fields: {required_fields}', status_code=400)
    
    student = Student.query.get(data['student_id'])
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    try:
        # Get all marks for the student in this term
        marks_records = Marks.query.filter_by(
            student_id=data['student_id'],
            term=data['term'],
            academic_year=data['academic_year']
        ).all()
        
        if not marks_records:
            return ResponseFormatter.error(
                'No marks found for this student, term, and academic year',
                status_code=404
            )
        
        # Calculate statistics
        total_marks = sum(mark.marks_obtained for mark in marks_records)
        average_percentage = sum(mark.percentage for mark in marks_records) / len(marks_records) if marks_records else 0
        
        # Get class rank (simplified - students with same percentage get same rank)
        class_marks = Marks.query.join(Student).filter(
            Student.class_id == student.class_id,
            Marks.term == data['term'],
            Marks.academic_year == data['academic_year']
        ).all()
        
        # Group by student and get average
        student_averages = {}
        for mark in class_marks:
            if mark.student_id not in student_averages:
                student_averages[mark.student_id] = []
            student_averages[mark.student_id].append(mark.percentage)
        
        # Calculate ranks
        student_avg_marks = {
            sid: sum(marks) / len(marks) for sid, marks in student_averages.items()
        }
        sorted_students = sorted(student_avg_marks.items(), key=lambda x: x[1], reverse=True)
        class_rank = next(
            (idx + 1 for idx, (sid, _) in enumerate(sorted_students) if sid == data['student_id']),
            None
        )
        
        # Check if report already exists
        existing_report = TermReport.query.filter_by(
            student_id=data['student_id'],
            term=data['term'],
            academic_year=data['academic_year']
        ).first()
        
        if existing_report:
            existing_report.total_marks = total_marks
            existing_report.average_percentage = average_percentage
            existing_report.class_rank = class_rank
            existing_report.teacher_remarks = data.get('teacher_remarks')
            report = existing_report
        else:
            report = TermReport(
                student_id=data['student_id'],
                term=data['term'],
                academic_year=data['academic_year'],
                total_marks=total_marks,
                average_percentage=average_percentage,
                class_rank=class_rank,
                teacher_remarks=data.get('teacher_remarks')
            )
            db.session.add(report)
        
        db.session.commit()
        
        return ResponseFormatter.success(
            data=report.to_dict(),
            message='Term report generated successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error generating report: {str(e)}', status_code=500)


@reports_bp.route('/student/<int:student_id>/term/<int:term>', methods=['GET'])
@token_required
def get_term_report(current_user, student_id, term):
    """Get term report for a student"""
    academic_year = request.args.get('academic_year', '2023/2024')
    
    report = TermReport.query.filter_by(
        student_id=student_id,
        term=term,
        academic_year=academic_year
    ).first()
    
    if not report:
        return ResponseFormatter.error('Report not found', status_code=404)
    
    return ResponseFormatter.success(data=report.to_dict())


@reports_bp.route('/student/<int:student_id>', methods=['GET'])
@token_required
def get_student_reports(current_user, student_id):
    """Get all reports for a student"""
    page, per_page = get_pagination_params()
    
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    query = TermReport.query.filter_by(student_id=student_id).order_by(
        TermReport.academic_year.desc(),
        TermReport.term.desc()
    )
    
    result = paginate_query(query, page, per_page)
    return ResponseFormatter.success(data=result)


@reports_bp.route('/class/<int:class_id>/term/<int:term>', methods=['GET'])
@token_required
@teacher_or_admin_required
def get_class_term_report(current_user, class_id, term):
    """Get term reports for all students in a class"""
    page, per_page = get_pagination_params()
    academic_year = request.args.get('academic_year', '2023/2024')
    
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return ResponseFormatter.error('Class not found', status_code=404)
    
    query = TermReport.query.join(Student).filter(
        Student.class_id == class_id,
        TermReport.term == term,
        TermReport.academic_year == academic_year
    ).order_by(TermReport.class_rank)
    
    result = paginate_query(query, page, per_page)
    return ResponseFormatter.success(data=result)


@reports_bp.route('/performance-analytics/<int:student_id>', methods=['GET'])
@token_required
def get_performance_analytics(current_user, student_id):
    """Get performance analytics for a student"""
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    # Get all reports
    reports = TermReport.query.filter_by(student_id=student_id).order_by(
        TermReport.academic_year,
        TermReport.term
    ).all()
    
    if not reports:
        return ResponseFormatter.error('No reports found for this student', status_code=404)
    
    # Prepare trend data
    trend_data = [
        {
            'academic_year': r.academic_year,
            'term': r.term,
            'average_percentage': round(r.average_percentage, 2),
            'class_rank': r.class_rank
        }
        for r in reports
    ]
    
    # Calculate improvement trend
    if len(reports) > 1:
        first_avg = reports[0].average_percentage
        last_avg = reports[-1].average_percentage
        improvement = round(last_avg - first_avg, 2)
    else:
        improvement = 0
    
    return ResponseFormatter.success(data={
        'student_id': student_id,
        'name': f"{student.user.first_name} {student.user.last_name}",
        'trend': trend_data,
        'improvement': improvement,
        'current_average': round(reports[-1].average_percentage, 2) if reports else 0
    })


@reports_bp.route('/public/totals', methods=['GET'])
def public_totals():
    """Public endpoint returning basic totals (no auth)"""
    try:
        from datetime import date

        total_students = Student.query.count()
        total_classes = Class.query.count()

        teacher_role = Role.query.filter_by(name='teacher').first()
        total_teachers = User.query.filter_by(role_id=teacher_role.id).count() if teacher_role else 0

        today = date.today()
        present_today = Attendance.query.filter_by(date=today, status=AttendanceStatus.PRESENT).count()

        data = {
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_classes': total_classes,
            'present_today': present_today,
        }
        return ResponseFormatter.success(data=data)
    except Exception as e:
        return ResponseFormatter.error(f'Error fetching public totals: {str(e)}', status_code=500)
