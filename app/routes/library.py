from flask import Blueprint, request
from app import db
from app.models import Book, BorrowRecord, Student
from app.utils.decorators import token_required, admin_required, validate_request_json, get_pagination_params, paginate_query
from app.utils.helpers import ResponseFormatter

library_bp = Blueprint('library', __name__)


@library_bp.route('/books', methods=['POST'])
@token_required
@admin_required
def add_book(current_user):
    data = request.get_json()
    required_fields = ['title', 'total_copies']
    for field in required_fields:
        if field not in data or data[field] is None:
            return ResponseFormatter.error(f'Missing required field: {field}', status_code=400)

    try:
        book = Book(
            title=data['title'],
            author=data.get('author'),
            isbn=data.get('isbn'),
            total_copies=data['total_copies'],
            available_copies=data['total_copies'],
            category=data.get('category'),
            publisher=data.get('publisher')
        )
        db.session.add(book)
        db.session.commit()
        return ResponseFormatter.success(data=book.to_dict(), message='Book added successfully', status_code=201)
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error adding book: {str(e)}', status_code=500)


@library_bp.route('/books', methods=['GET'])
@token_required
def get_books(current_user):
    page, per_page = get_pagination_params()
    query = Book.query

    category = request.args.get('category')
    if category:
        query = query.filter_by(category=category)

    result = paginate_query(query.order_by(Book.title), page, per_page)
    return ResponseFormatter.success(data=result)


@library_bp.route('/borrow', methods=['POST'])
@token_required
@validate_request_json('book_id', 'student_id', 'due_date')
def borrow_book(current_user):
    data = request.get_json()

    book = Book.query.get(data['book_id'])
    if not book:
        return ResponseFormatter.error('Book not found', status_code=404)
    if book.available_copies < 1:
        return ResponseFormatter.error('No copies available', status_code=400)

    student = Student.query.get(data['student_id'])
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)

    try:
        borrow_record = BorrowRecord(
            book_id=book.id,
            student_id=student.id,
            borrowed_by_id=current_user.id,
            due_date=data['due_date']
        )
        book.available_copies -= 1
        db.session.add(borrow_record)
        db.session.commit()
        return ResponseFormatter.success(data=borrow_record.to_dict(), message='Book borrowed successfully', status_code=201)
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error borrowing book: {str(e)}', status_code=500)


@library_bp.route('/return/<int:borrow_id>', methods=['POST'])
@token_required
def return_book(current_user, borrow_id):
    borrow_record = BorrowRecord.query.get(borrow_id)
    if not borrow_record:
        return ResponseFormatter.error('Borrow record not found', status_code=404)
    if borrow_record.status == 'returned':
        return ResponseFormatter.error('Book already returned', status_code=400)

    try:
        borrow_record.status = 'returned'
        borrow_record.returned_date = db.func.now()
        book = Book.query.get(borrow_record.book_id)
        if book:
            book.available_copies += 1
        db.session.commit()
        return ResponseFormatter.success(data=borrow_record.to_dict(), message='Book returned successfully')
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error returning book: {str(e)}', status_code=500)


@library_bp.route('/records', methods=['GET'])
@token_required
def get_borrow_records(current_user):
    page, per_page = get_pagination_params()
    query = BorrowRecord.query

    student_id = request.args.get('student_id', type=int)
    status = request.args.get('status')
    if student_id:
        query = query.filter_by(student_id=student_id)
    if status:
        query = query.filter_by(status=status)

    result = paginate_query(query.order_by(BorrowRecord.borrow_date.desc()), page, per_page)
    return ResponseFormatter.success(data=result)
