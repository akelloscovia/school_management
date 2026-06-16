from flask import Blueprint, request
from datetime import datetime
from app import db
from app.models import FeePayment, Expense, Student
from app.utils.decorators import (
    token_required, accountant_or_admin_required, admin_required,
    validate_request_json, get_pagination_params, paginate_query
)
from app.utils.helpers import ResponseFormatter

finance_bp = Blueprint('finance', __name__)


@finance_bp.route('/payments', methods=['POST'])
@token_required
@validate_request_json('student_id', 'amount', 'payment_method', 'academic_year')
def record_payment(current_user):
    data = request.get_json()

    student = Student.query.get(data['student_id'])
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)

    try:
        receipt_number = f"RCPT{student.id}{int(datetime.utcnow().timestamp())}"
        payment = FeePayment(
            student_id=data['student_id'],
            amount=data['amount'],
            payment_method=data['payment_method'],
            receipt_number=receipt_number,
            academic_year=data['academic_year'],
            term=data.get('term'),
            description=data.get('description'),
            recorded_by_id=current_user.id
        )
        db.session.add(payment)
        db.session.commit()

        return ResponseFormatter.success(data=payment.to_dict(), message='Payment recorded successfully', status_code=201)
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error recording payment: {str(e)}', status_code=500)


@finance_bp.route('/payments', methods=['GET'])
@token_required
def get_payments(current_user):
    page, per_page = get_pagination_params()
    query = FeePayment.query

    student_id = request.args.get('student_id', type=int)
    academic_year = request.args.get('academic_year')
    if student_id:
        query = query.filter_by(student_id=student_id)
    if academic_year:
        query = query.filter_by(academic_year=academic_year)

    result = paginate_query(query.order_by(FeePayment.payment_date.desc()), page, per_page)
    return ResponseFormatter.success(data=result)


@finance_bp.route('/payments/<int:payment_id>', methods=['GET'])
@token_required
def get_payment(current_user, payment_id):
    payment = FeePayment.query.get(payment_id)
    if not payment:
        return ResponseFormatter.error('Payment not found', status_code=404)
    return ResponseFormatter.success(data=payment.to_dict())


@finance_bp.route('/students/<int:student_id>/balance', methods=['GET'])
@token_required
def get_student_balance(current_user, student_id):
    student = Student.query.get(student_id)
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)

    paid = db.session.query(db.func.coalesce(db.func.sum(FeePayment.amount), 0)).filter_by(student_id=student_id).scalar()
    return ResponseFormatter.success(data={
        'student_id': student_id,
        'amount_paid': float(paid),
        'balance': None
    })


@finance_bp.route('/expenses', methods=['POST'])
@token_required
@admin_required
def record_expense(current_user):
    data = request.get_json()
    required_fields = ['amount', 'category']
    for field in required_fields:
        if field not in data or data[field] is None:
            return ResponseFormatter.error(f'Missing required field: {field}', status_code=400)

    try:
        expense = Expense(
            amount=data['amount'],
            category=data['category'],
            expense_date=data.get('expense_date'),
            description=data.get('description'),
            recorded_by_id=current_user.id
        )
        db.session.add(expense)
        db.session.commit()

        return ResponseFormatter.success(data=expense.to_dict(), message='Expense recorded successfully', status_code=201)
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error recording expense: {str(e)}', status_code=500)


@finance_bp.route('/expenses', methods=['GET'])
@token_required
def get_expenses(current_user):
    page, per_page = get_pagination_params()
    query = Expense.query

    category = request.args.get('category')
    if category:
        query = query.filter_by(category=category)

    result = paginate_query(query.order_by(Expense.expense_date.desc()), page, per_page)
    return ResponseFormatter.success(data=result)
