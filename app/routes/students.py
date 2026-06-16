from flask import Blueprint, request
from datetime import datetime
from app import db
from app.models import Student, User, Role, StudentParent, StudentDocument, StudentTransfer, PromotionHistory
from app.utils.decorators import (
    token_required, admin_required, teacher_or_admin_required, validate_request_json,
    get_pagination_params, paginate_query
)
from app.utils.helpers import ResponseFormatter, generate_admission_number, calculate_attendance_percentage

students_bp = Blueprint('students', __name__)


@students_bp.route('', methods=['GET'])
@token_required
def get_all_students(current_user):
    """Get all students"""
    page, per_page = get_pagination_params()
    
    # Filter by class if specified
    class_id = request.args.get('class_id', type=int)
    query = Student.query
    
    if class_id:
        query = query.filter_by(class_id=class_id)
    
    if current_user.role.name == 'student':
        query = query.filter_by(user_id=current_user.id)
    elif current_user.role.name == 'parent':
        parent_students = StudentParent.query.filter_by(user_id=current_user.id).all()
        student_ids = [parent.student_id for parent in parent_students]
        query = query.filter(Student.id.in_(student_ids))
    
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    result = {
        'items': [item.to_dict(include_user=True) for item in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
        'per_page': per_page
    }
    return ResponseFormatter.success(data=result)


@students_bp.route('/<int:student_id>', methods=['GET'])
@token_required
def get_student(current_user, student_id):
    """Get student by ID"""
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    if current_user.role.name == 'student' and current_user.id != student.user_id:
        return ResponseFormatter.error('Insufficient permissions', status_code=403)
    if current_user.role.name == 'parent':
        parent_link = StudentParent.query.filter_by(student_id=student_id, user_id=current_user.id).first()
        if not parent_link:
            return ResponseFormatter.error('Insufficient permissions', status_code=403)
    
    return ResponseFormatter.success(data=student.to_dict(include_user=True))


@students_bp.route('/register', methods=['POST'])
@validate_request_json('first_name', 'last_name', 'email', 'password', 'date_of_birth', 'gender', 'class_id')
def register_student():
    """Register a student account and profile"""
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return ResponseFormatter.error('Email already registered', status_code=400)
    
    student_role = Role.query.filter_by(name='student').first()
    if not student_role:
        return ResponseFormatter.error('Student role not configured', status_code=500)
    
    try:
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            role_id=student_role.id
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()
        
        student = Student(
            user_id=user.id,
            admission_number=generate_admission_number(),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
            gender=data['gender'],
            address=data.get('address'),
            medical_info=data.get('medical_info'),
            photo_url=data.get('photo_url'),
            admission_status=data.get('admission_status', 'pending'),
            class_id=data['class_id']
        )
        db.session.add(student)
        db.session.commit()
        
        return ResponseFormatter.success(
            data=student.to_dict(include_user=True),
            message='Student registered successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error registering student: {str(e)}', status_code=500)


@students_bp.route('', methods=['POST'])
@token_required
@admin_required
def create_student(current_user):
    """Create a new student"""
    data = request.get_json()
    required_fields = ['first_name', 'last_name', 'email', 'password', 'date_of_birth', 'gender', 'class_id']
    for field in required_fields:
        if field not in data or data[field] is None:
            return ResponseFormatter.error(f'Missing required field: {field}', status_code=400)

    if User.query.filter_by(email=data['email']).first():
        return ResponseFormatter.error('Email already registered', status_code=400)
    
    student_role = Role.query.filter_by(name='student').first()
    if not student_role:
        return ResponseFormatter.error('Student role not configured', status_code=500)
    
    try:
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            role_id=student_role.id
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()
        
        student = Student(
            user_id=user.id,
            admission_number=generate_admission_number(),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
            gender=data['gender'],
            address=data.get('address'),
            medical_info=data.get('medical_info'),
            photo_url=data.get('photo_url'),
            admission_status=data.get('admission_status', 'pending'),
            class_id=data['class_id']
        )
        db.session.add(student)
        db.session.commit()
        
        return ResponseFormatter.success(
            data=student.to_dict(include_user=True),
            message='Student created successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error creating student: {str(e)}', status_code=500)


@students_bp.route('/<int:student_id>', methods=['PUT'])
@token_required
@admin_required
def update_student(current_user, student_id):
    """Update student"""
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    data = request.get_json()
    
    try:
        student.address = data.get('address', student.address)
        student.gender = data.get('gender', student.gender)
        
        if 'class_id' in data:
            student.class_id = data['class_id']
        
        # Update user fields
        if 'first_name' in data:
            student.user.first_name = data['first_name']
        if 'last_name' in data:
            student.user.last_name = data['last_name']
        if 'phone' in data:
            student.user.phone = data['phone']
        
        db.session.commit()
        return ResponseFormatter.success(data=student.to_dict(include_user=True), message='Student updated successfully')
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error updating student: {str(e)}', status_code=500)


@students_bp.route('/<int:student_id>/parents', methods=['GET'])
@token_required
def get_student_parents(current_user, student_id):
    """Get student's parents"""
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    parents = StudentParent.query.filter_by(student_id=student_id).all()
    return ResponseFormatter.success(data=[parent.to_dict() for parent in parents])


@students_bp.route('/<int:student_id>/parents', methods=['POST'])
@token_required
@admin_required
@validate_request_json('parent_name', 'relationship', 'phone')
def add_student_parent(current_user, student_id):
    """Add parent to student"""
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    data = request.get_json()
    
    try:
        parent = StudentParent(
            student_id=student_id,
            user_id=data.get('user_id'),
            parent_name=data['parent_name'],
            relationship=data['relationship'],
            phone=data['phone'],
            email=data.get('email'),
            occupation=data.get('occupation'),
            address=data.get('address'),
            is_primary_contact=data.get('is_primary_contact', False)
        )
        db.session.add(parent)
        db.session.commit()
        
        return ResponseFormatter.success(
            data=parent.to_dict(),
            message='Parent added successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error adding parent: {str(e)}', status_code=500)


@students_bp.route('/<int:student_id>/documents', methods=['POST'])
@token_required
@admin_required
@validate_request_json('title', 'document_type', 'file_name')
def upload_student_document(current_user, student_id):
    """Upload document metadata for a student"""
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    data = request.get_json()
    
    try:
        document = StudentDocument(
            student_id=student_id,
            title=data['title'],
            document_type=data['document_type'],
            file_name=data['file_name'],
            file_url=data.get('file_url'),
            uploaded_by_id=current_user.id
        )
        db.session.add(document)
        db.session.commit()
        
        return ResponseFormatter.success(
            data=document.to_dict(),
            message='Document uploaded successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error uploading document: {str(e)}', status_code=500)


@students_bp.route('/<int:student_id>/documents', methods=['GET'])
@token_required
def get_student_documents(current_user, student_id):
    """Get student documents"""
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    documents = StudentDocument.query.filter_by(student_id=student_id).all()
    return ResponseFormatter.success(data=[doc.to_dict() for doc in documents])


@students_bp.route('/<int:student_id>/transfers', methods=['POST'])
@token_required
@admin_required
@validate_request_json('to_class_id', 'reason')
def create_student_transfer(current_user, student_id):
    """Create a transfer record for a student"""
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    data = request.get_json()
    
    try:
        transfer = StudentTransfer(
            student_id=student_id,
            from_class_id=student.class_id,
            to_class_id=data['to_class_id'],
            reason=data['reason'],
            status=data.get('status', 'pending'),
            parent_contact=data.get('parent_contact'),
            medical_info=data.get('medical_info', student.medical_info),
            photo_url=data.get('photo_url', student.photo_url),
            comments=data.get('comments')
        )
        student.class_id = data['to_class_id']
        db.session.add(transfer)
        db.session.commit()
        
        return ResponseFormatter.success(
            data=transfer.to_dict(),
            message='Transfer record created successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error creating transfer record: {str(e)}', status_code=500)


@students_bp.route('/<int:student_id>/transfers', methods=['GET'])
@token_required
def get_student_transfers(current_user, student_id):
    """Get transfer records for a student"""
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    transfers = StudentTransfer.query.filter_by(student_id=student_id).all()
    return ResponseFormatter.success(data=[t.to_dict() for t in transfers])


@students_bp.route('/<int:student_id>/promote', methods=['POST'])
@token_required
@admin_required
@validate_request_json('to_class_id')
def promote_student(current_user, student_id):
    """Promote a student to the next class"""
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    data = request.get_json()
    from_class_id = student.class_id
    
    try:
        student.class_id = data['to_class_id']
        promotion = PromotionHistory(
            student_id=student_id,
            from_class_id=from_class_id,
            to_class_id=data['to_class_id'],
            promoted_by_id=current_user.id,
            remarks=data.get('remarks')
        )
        db.session.add(promotion)
        db.session.commit()
        
        return ResponseFormatter.success(
            data=promotion.to_dict(),
            message='Student promoted successfully',
            status_code=200
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error promoting student: {str(e)}', status_code=500)


@students_bp.route('/<int:student_id>/promotions', methods=['GET'])
@token_required
def get_student_promotions(current_user, student_id):
    """Get promotion history for a student"""
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    promotions = PromotionHistory.query.filter_by(student_id=student_id).all()
    return ResponseFormatter.success(data=[p.to_dict() for p in promotions])


@students_bp.route('/<int:student_id>/performance', methods=['GET'])
@token_required
def get_student_performance(current_user, student_id):
    """Get student performance summary"""
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    from app.utils.helpers import calculate_average_marks
    
    attendance_percentage = calculate_attendance_percentage(student_id)
    average_marks = calculate_average_marks(student_id)
    
    data = {
        'student_id': student_id,
        'admission_number': student.admission_number,
        'name': f"{student.user.first_name} {student.user.last_name}",
        'attendance_percentage': attendance_percentage,
        'average_marks': average_marks
    }
    
    return ResponseFormatter.success(data=data)


@students_bp.route('/<int:student_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_student(current_user, student_id):
    """Delete a student and their associated user account"""
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)
    
    try:
        user_id = student.user_id
        
        # Delete student first (due to foreign key constraints)
        db.session.delete(student)
        
        # Delete associated user
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
        
        db.session.commit()
        
        return ResponseFormatter.success(
            message='Student deleted successfully',
            status_code=200
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error deleting student: {str(e)}', status_code=500)
