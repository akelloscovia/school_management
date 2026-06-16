from flask import Blueprint, request
from app import db
from app.models import Class, Subject, User, TimetableEntry, ClassNote
from app.utils.decorators import (
    token_required, admin_required, teacher_or_admin_required, validate_request_json,
    get_pagination_params, paginate_query
)
from app.utils.helpers import ResponseFormatter

classes_bp = Blueprint('classes', __name__)


@classes_bp.route('', methods=['GET'])
@token_required
def get_all_classes(current_user):
    """Get all classes"""
    page, per_page = get_pagination_params()
    
    academic_year = request.args.get('academic_year')
    level = request.args.get('level')
    
    query = Class.query
    
    if academic_year:
        query = query.filter_by(academic_year=academic_year)
    if level:
        query = query.filter_by(level=level)
    
    query = query.order_by(Class.created_at.desc())
    result = paginate_query(query, page, per_page)
    
    return ResponseFormatter.success(data=result)


@classes_bp.route('/<int:class_id>', methods=['GET'])
@token_required
def get_class(current_user, class_id):
    """Get class details"""
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return ResponseFormatter.error('Class not found', status_code=404)
    
    return ResponseFormatter.success(data=class_obj.to_dict(include_teacher=True))


@classes_bp.route('', methods=['POST'])
@token_required
@admin_required
@validate_request_json('name', 'level', 'academic_year')
def create_class(current_user):
    """Create a new class"""
    data = request.get_json()
    
    # Check if class already exists
    existing = Class.query.filter_by(name=data['name'], academic_year=data['academic_year']).first()
    if existing:
        return ResponseFormatter.error('Class already exists', status_code=400)
    
    try:
        class_obj = Class(
            name=data['name'],
            level=data['level'],
            teacher_id=data.get('teacher_id'),
            academic_year=data['academic_year'],
            max_capacity=data.get('max_capacity', 50),
            description=data.get('description')
        )
        db.session.add(class_obj)
        db.session.commit()
        
        return ResponseFormatter.success(
            data=class_obj.to_dict(include_teacher=True),
            message='Class created successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error creating class: {str(e)}', status_code=500)


@classes_bp.route('/<int:class_id>', methods=['PUT'])
@token_required
@admin_required
def update_class(current_user, class_id):
    """Update class"""
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return ResponseFormatter.error('Class not found', status_code=404)
    
    data = request.get_json()
    
    try:
        class_obj.name = data.get('name', class_obj.name)
        class_obj.level = data.get('level', class_obj.level)
        class_obj.max_capacity = data.get('max_capacity', class_obj.max_capacity)
        class_obj.description = data.get('description', class_obj.description)
        
        if 'teacher_id' in data:
            teacher = User.query.get(data['teacher_id'])
            if teacher and teacher.role.name == 'teacher':
                class_obj.teacher_id = data['teacher_id']
            else:
                return ResponseFormatter.error('Invalid teacher ID', status_code=400)
        
        db.session.commit()
        
        return ResponseFormatter.success(
            data=class_obj.to_dict(include_teacher=True),
            message='Class updated successfully'
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error updating class: {str(e)}', status_code=500)


@classes_bp.route('/<int:class_id>/subjects', methods=['GET'])
@token_required
def get_class_subjects(current_user, class_id):
    """Get subjects for a class"""
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return ResponseFormatter.error('Class not found', status_code=404)
    
    subjects = Subject.query.filter_by(class_id=class_id).all()
    return ResponseFormatter.success(data=[s.to_dict() for s in subjects])


@classes_bp.route('/<int:class_id>/timetable', methods=['POST'])
@token_required
@admin_required
@validate_request_json('subject_id', 'teacher_id', 'day_of_week', 'start_time', 'end_time', 'academic_year')
def add_timetable_entry(current_user, class_id):
    """Add a timetable entry for a class"""
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return ResponseFormatter.error('Class not found', status_code=404)
    
    data = request.get_json()
    entry = TimetableEntry(
        class_id=class_id,
        subject_id=data['subject_id'],
        teacher_id=data['teacher_id'],
        day_of_week=data['day_of_week'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        venue=data.get('venue'),
        academic_year=data['academic_year']
    )
    db.session.add(entry)
    db.session.commit()
    
    return ResponseFormatter.success(data=entry.to_dict(), message='Timetable entry created successfully', status_code=201)


@classes_bp.route('/<int:class_id>/timetable', methods=['GET'])
@token_required
def get_class_timetable(current_user, class_id):
    """Get timetable entries for a class"""
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return ResponseFormatter.error('Class not found', status_code=404)
    
    entries = TimetableEntry.query.filter_by(class_id=class_id).order_by(TimetableEntry.day_of_week, TimetableEntry.start_time).all()
    return ResponseFormatter.success(data=[entry.to_dict() for entry in entries])


@classes_bp.route('/<int:class_id>/notes', methods=['POST'])
@token_required
@teacher_or_admin_required
@validate_request_json('title')
def add_class_note(current_user, class_id):
    """Upload or add a note/resource for a class"""
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return ResponseFormatter.error('Class not found', status_code=404)
    
    data = request.get_json()
    note = ClassNote(
        class_id=class_id,
        subject_id=data.get('subject_id'),
        title=data['title'],
        description=data.get('description'),
        file_url=data.get('file_url'),
        uploaded_by_id=current_user.id
    )
    db.session.add(note)
    db.session.commit()
    
    return ResponseFormatter.success(data=note.to_dict(), message='Class note uploaded successfully', status_code=201)


@classes_bp.route('/<int:class_id>/notes', methods=['GET'])
@token_required
def get_class_notes(current_user, class_id):
    """Get notes and resources for a class"""
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return ResponseFormatter.error('Class not found', status_code=404)
    
    notes = ClassNote.query.filter_by(class_id=class_id).order_by(ClassNote.uploaded_at.desc()).all()
    return ResponseFormatter.success(data=[note.to_dict() for note in notes])


@classes_bp.route('/<int:class_id>/subjects', methods=['POST'])
@token_required
@admin_required
@validate_request_json('name', 'code')
def add_subject_to_class(current_user, class_id):
    """Add subject to class"""
    class_obj = Class.query.get(class_id)
    if not class_obj:
        return ResponseFormatter.error('Class not found', status_code=404)
    
    data = request.get_json()
    
    # Check if subject code already exists
    existing = Subject.query.filter_by(code=data['code']).first()
    if existing:
        return ResponseFormatter.error('Subject code already exists', status_code=400)
    
    try:
        subject = Subject(
            name=data['name'],
            code=data['code'],
            class_id=class_id,
            description=data.get('description'),
            credit_hours=data.get('credit_hours', 40)
        )
        db.session.add(subject)
        db.session.commit()
        
        return ResponseFormatter.success(
            data=subject.to_dict(),
            message='Subject added successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error adding subject: {str(e)}', status_code=500)


@classes_bp.route('/subject/<int:subject_id>', methods=['PUT'])
@token_required
@admin_required
def update_subject(current_user, subject_id):
    """Update subject"""
    subject = Subject.query.get(subject_id)
    if not subject:
        return ResponseFormatter.error('Subject not found', status_code=404)
    
    data = request.get_json()
    
    try:
        subject.name = data.get('name', subject.name)
        subject.description = data.get('description', subject.description)
        subject.credit_hours = data.get('credit_hours', subject.credit_hours)
        
        db.session.commit()
        
        return ResponseFormatter.success(
            data=subject.to_dict(),
            message='Subject updated successfully'
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error updating subject: {str(e)}', status_code=500)
