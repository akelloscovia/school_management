from flask import Blueprint, request
from app import db
from app.models import BusRoute, BoardingAssignment, Dormitory, DormitoryAllocation, Student
from app.utils.decorators import token_required, admin_required, validate_request_json, get_pagination_params, paginate_query
from app.utils.helpers import ResponseFormatter

transport_bp = Blueprint('transport', __name__)


@transport_bp.route('/routes', methods=['POST'])
@token_required
@admin_required
def create_bus_route(current_user):
    data = request.get_json()
    required_fields = ['name']
    for field in required_fields:
        if field not in data or data[field] is None:
            return ResponseFormatter.error(f'Missing required field: {field}', status_code=400)

    try:
        route = BusRoute(
            name=data['name'],
            driver_name=data.get('driver_name'),
            driver_phone=data.get('driver_phone'),
            route_description=data.get('route_description'),
            capacity=data.get('capacity', 50),
            active=data.get('active', True)
        )
        db.session.add(route)
        db.session.commit()
        return ResponseFormatter.success(data=route.to_dict(), message='Bus route created successfully', status_code=201)
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error creating bus route: {str(e)}', status_code=500)


@transport_bp.route('/routes', methods=['GET'])
@token_required
def get_bus_routes(current_user):
    page, per_page = get_pagination_params()
    query = BusRoute.query
    active = request.args.get('active')
    if active is not None:
        query = query.filter_by(active=active.lower() == 'true')
    result = paginate_query(query.order_by(BusRoute.name), page, per_page)
    return ResponseFormatter.success(data=result)


@transport_bp.route('/boarding', methods=['POST'])
@token_required
@admin_required
def assign_boarding(current_user):
    data = request.get_json()
    required_fields = ['student_id', 'bus_route_id', 'boarding_point']
    for field in required_fields:
        if field not in data or data[field] is None:
            return ResponseFormatter.error(f'Missing required field: {field}', status_code=400)

    student = Student.query.get(data['student_id'])
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)

    route = BusRoute.query.get(data['bus_route_id'])
    if not route:
        return ResponseFormatter.error('Bus route not found', status_code=404)

    try:
        assignment = BoardingAssignment(
            student_id=data['student_id'],
            bus_route_id=data['bus_route_id'],
            boarding_point=data['boarding_point'],
            active=data.get('active', True)
        )
        db.session.add(assignment)
        db.session.commit()
        return ResponseFormatter.success(data=assignment.to_dict(), message='Boarding assigned successfully', status_code=201)
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error assigning boarding: {str(e)}', status_code=500)


@transport_bp.route('/boarding', methods=['GET'])
@token_required
def get_boarding_assignments(current_user):
    page, per_page = get_pagination_params()
    student_id = request.args.get('student_id', type=int)
    query = BoardingAssignment.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    result = paginate_query(query.order_by(BoardingAssignment.assigned_at.desc()), page, per_page)
    return ResponseFormatter.success(data=result)


@transport_bp.route('/dormitories', methods=['POST'])
@token_required
@admin_required
def create_dormitory(current_user):
    data = request.get_json()
    required_fields = ['name', 'capacity']
    for field in required_fields:
        if field not in data or data[field] is None:
            return ResponseFormatter.error(f'Missing required field: {field}', status_code=400)

    try:
        dorm = Dormitory(
            name=data['name'],
            block=data.get('block'),
            capacity=data['capacity'],
            description=data.get('description')
        )
        db.session.add(dorm)
        db.session.commit()
        return ResponseFormatter.success(data=dorm.to_dict(), message='Dormitory created successfully', status_code=201)
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error creating dormitory: {str(e)}', status_code=500)


@transport_bp.route('/dormitories', methods=['GET'])
@token_required
def get_dormitories(current_user):
    page, per_page = get_pagination_params()
    result = paginate_query(Dormitory.query.order_by(Dormitory.name), page, per_page)
    return ResponseFormatter.success(data=result)


@transport_bp.route('/dormitory-allocations', methods=['POST'])
@token_required
@admin_required
def allocate_dormitory(current_user):
    data = request.get_json()
    required_fields = ['student_id', 'dormitory_id', 'room_number']
    for field in required_fields:
        if field not in data or data[field] is None:
            return ResponseFormatter.error(f'Missing required field: {field}', status_code=400)

    student = Student.query.get(data['student_id'])
    if not student:
        return ResponseFormatter.error('Student not found', status_code=404)

    dorm = Dormitory.query.get(data['dormitory_id'])
    if not dorm:
        return ResponseFormatter.error('Dormitory not found', status_code=404)

    try:
        allocation = DormitoryAllocation(
            student_id=data['student_id'],
            dormitory_id=data['dormitory_id'],
            room_number=data['room_number'],
            active=data.get('active', True)
        )
        db.session.add(allocation)
        db.session.commit()
        return ResponseFormatter.success(data=allocation.to_dict(), message='Dormitory allocated successfully', status_code=201)
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error allocating dormitory: {str(e)}', status_code=500)


@transport_bp.route('/dormitory-allocations', methods=['GET'])
@token_required
def get_dormitory_allocations(current_user):
    page, per_page = get_pagination_params()
    student_id = request.args.get('student_id', type=int)
    query = DormitoryAllocation.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    result = paginate_query(query.order_by(DormitoryAllocation.assigned_at.desc()), page, per_page)
    return ResponseFormatter.success(data=result)
