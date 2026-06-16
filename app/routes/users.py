from flask import Blueprint, request
from app import db
from app.models import User, Role
from app.utils.decorators import (
    token_required, admin_required, validate_request_json,
    get_pagination_params, paginate_query
)
from app.utils.helpers import ResponseFormatter

users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['GET'])
@token_required
@admin_required
def get_all_users(current_user):
    """Get all users with pagination"""
    page, per_page = get_pagination_params()
    query = User.query
    
    # Filter by role if specified
    role_name = request.args.get('role')
    if role_name:
        query = query.join(Role).filter(Role.name == role_name)
    
    result = paginate_query(query, page, per_page)
    return ResponseFormatter.success(data=result)


@users_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    """Get user by ID"""
    # Users can only view their own profile unless admin
    if current_user.id != user_id and current_user.role.name != 'admin':
        return ResponseFormatter.error('Insufficient permissions', status_code=403)
    
    user = User.query.get(user_id)
    if not user:
        return ResponseFormatter.error('User not found', status_code=404)
    
    return ResponseFormatter.success(data=user.to_dict())


@users_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
@validate_request_json('first_name', 'last_name', 'phone')
def update_user(current_user, user_id):
    """Update user"""
    # Users can only update their own profile unless admin
    if current_user.id != user_id and current_user.role.name != 'admin':
        return ResponseFormatter.error('Insufficient permissions', status_code=403)
    
    user = User.query.get(user_id)
    if not user:
        return ResponseFormatter.error('User not found', status_code=404)
    
    data = request.get_json()
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.phone = data.get('phone', user.phone)
    
    try:
        db.session.commit()
        return ResponseFormatter.success(data=user.to_dict(), message='User updated successfully')
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error updating user: {str(e)}', status_code=500)


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(current_user, user_id):
    """Delete user (soft delete)"""
    user = User.query.get(user_id)
    if not user:
        return ResponseFormatter.error('User not found', status_code=404)
    
    try:
        user.is_active = False
        db.session.commit()
        return ResponseFormatter.success(message='User deactivated successfully')
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error deleting user: {str(e)}', status_code=500)


@users_bp.route('/by-role/<role_name>', methods=['GET'])
@token_required
@admin_required
def get_users_by_role(current_user, role_name):
    """Get all users with a specific role"""
    page, per_page = get_pagination_params()
    
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return ResponseFormatter.error('Role not found', status_code=404)
    
    query = User.query.filter_by(role_id=role.id)
    result = paginate_query(query, page, per_page)
    
    return ResponseFormatter.success(data=result)


@users_bp.route('/<int:user_id>/activate', methods=['POST'])
@token_required
@admin_required
def activate_user(current_user, user_id):
    """Activate a user"""
    user = User.query.get(user_id)
    if not user:
        return ResponseFormatter.error('User not found', status_code=404)
    
    try:
        user.is_active = True
        db.session.commit()
        return ResponseFormatter.success(data=user.to_dict(), message='User activated successfully')
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error activating user: {str(e)}', status_code=500)
