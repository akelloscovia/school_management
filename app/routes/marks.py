from flask import Blueprint, request
from app import db
from app.models import Marks, TermReport, Subject, Student
from app.utils.decorators import (
    token_required, teacher_or_admin_required, validate_request_json,
    get_pagination_params, paginate_query
)
from app.utils.helpers import ResponseFormatter

marks_bp = Blueprint('marks', __name__)


@marks_bp.route('', methods=['POST'])
@token_required
@teacher_or_admin_required
@validate_request_json('student_id', 'subject_id', 'term', 'exam_type', 'marks_obtained', 'total_marks')
def record_marks(current_user):
    """Record marks for a student"""
    data = request.get_json()
    
    student = Student.query.get(data['student_id'])
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    subject = Subject.query.get(data['subject_id'])
    if not subject:
        return ResponseFormatter.error('Subject not found', status_code=404)
    
    # Check if marks already exist
    existing = Marks.query.filter_by(
        student_id=data['student_id'],
        subject_id=data['subject_id'],
        term=data['term'],
        exam_type=data['exam_type']
    ).first()
    
    try:
        if existing:
            existing.marks_obtained = data['marks_obtained']
            existing.total_marks = data.get('total_marks', existing.total_marks)
            marks = existing
        else:
            marks = Marks(
                student_id=data['student_id'],
                subject_id=data['subject_id'],
                term=data['term'],
                exam_type=data['exam_type'],
                marks_obtained=data['marks_obtained'],
                total_marks=data.get('total_marks', 100),
                academic_year=data.get('academic_year', '2023/2024'),
                recorded_by_id=current_user.id
            )
            db.session.add(marks)
        
        marks.calculate_percentage()
        marks.assign_grade()
        
        db.session.commit()
        
        return ResponseFormatter.success(
            data=marks.to_dict(),
            message='Marks recorded successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error recording marks: {str(e)}', status_code=500)


@marks_bp.route('', methods=['GET'])
@token_required
def list_marks(current_user):
    """List marks filtered by query params (class_id, student_id, subject_id, term)"""
    page, per_page = get_pagination_params()

    class_id = request.args.get('class_id', type=int)
    student_id = request.args.get('student_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    term = request.args.get('term', type=int)

    query = Marks.query

    if class_id:
        # join student to filter by class
        query = query.join(Student).filter(Student.class_id == class_id)
    if student_id:
        query = query.filter_by(student_id=student_id)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    if term:
        query = query.filter_by(term=term)

    query = query.order_by(Marks.created_at.desc())
    result = paginate_query(query, page, per_page)
    return ResponseFormatter.success(data=result)


@marks_bp.route('/student/<int:student_id>', methods=['GET'])
@token_required
def get_student_marks(current_user, student_id):
    """Get all marks for a student"""
    page, per_page = get_pagination_params()
    
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    term = request.args.get('term', type=int)
    academic_year = request.args.get('academic_year')
    
    query = Marks.query.filter_by(student_id=student_id)
    
    if term:
        query = query.filter_by(term=term)
    if academic_year:
        query = query.filter_by(academic_year=academic_year)
    
    query = query.order_by(Marks.created_at.desc())
    result = paginate_query(query, page, per_page)
    
    return ResponseFormatter.success(data=result)


@marks_bp.route('/subject/<int:subject_id>/term/<int:term>', methods=['GET'])
@token_required
@teacher_or_admin_required
def get_subject_term_marks(current_user, subject_id, term):
    """Get all marks for a subject in a term"""
    page, per_page = get_pagination_params()
    
    subject = Subject.query.get(subject_id)
    if not subject:
        return ResponseFormatter.error('Subject not found', status_code=404)
    
    query = Marks.query.filter_by(subject_id=subject_id, term=term).order_by(Marks.marks_obtained.desc())
    result = paginate_query(query, page, per_page)
    
    return ResponseFormatter.success(data=result)


@marks_bp.route('/<int:marks_id>', methods=['PUT'])
@token_required
@teacher_or_admin_required
def update_marks(current_user, marks_id):
    """Update marks record"""
    marks = Marks.query.get(marks_id)
    if not marks:
        return ResponseFormatter.error('Marks record not found', status_code=404)
    
    data = request.get_json()
    
    try:
        if 'marks_obtained' in data:
            marks.marks_obtained = data['marks_obtained']
        if 'total_marks' in data:
            marks.total_marks = data['total_marks']
        
        marks.calculate_percentage()
        marks.assign_grade()
        
        db.session.commit()
        
        return ResponseFormatter.success(
            data=marks.to_dict(),
            message='Marks updated successfully'
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error updating marks: {str(e)}', status_code=500)


@marks_bp.route('/bulk', methods=['POST'])
@token_required
@teacher_or_admin_required
@validate_request_json('subject_id', 'term', 'exam_type', 'marks_list')
def bulk_record_marks(current_user):
    """Record marks for multiple students"""
    data = request.get_json()
    
    subject = Subject.query.get(data['subject_id'])
    if not subject:
        return ResponseFormatter.error('Subject not found', status_code=404)
    
    marks_list = data['marks_list']
    created_count = 0
    updated_count = 0
    errors = []
    
    try:
        for mark_entry in marks_list:
            student_id = mark_entry.get('student_id')
            marks_obtained = mark_entry.get('marks_obtained')
            
            student = Student.query.get(student_id)
            if not student:
                errors.append(f"Student {student_id} not found")
                continue
            
            existing = Marks.query.filter_by(
                student_id=student_id,
                subject_id=data['subject_id'],
                term=data['term'],
                exam_type=data['exam_type']
            ).first()
            
            if existing:
                existing.marks_obtained = marks_obtained
                updated_count += 1
            else:
                mark = Marks(
                    student_id=student_id,
                    subject_id=data['subject_id'],
                    term=data['term'],
                    exam_type=data['exam_type'],
                    marks_obtained=marks_obtained,
                    total_marks=data.get('total_marks', 100),
                    academic_year=data.get('academic_year', '2023/2024'),
                    recorded_by_id=current_user.id
                )
                mark.calculate_percentage()
                mark.assign_grade()
                db.session.add(mark)
                created_count += 1
        
        db.session.commit()
        
        return ResponseFormatter.success(
            data={
                'created': created_count,
                'updated': updated_count,
                'errors': errors
            },
            message='Bulk marks recorded successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error recording marks: {str(e)}', status_code=500)
