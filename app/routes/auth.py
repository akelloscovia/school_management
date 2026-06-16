from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app import db
from app.models import User, Role
from app.utils.decorators import validate_request_json, token_required
from app.utils.helpers import ResponseFormatter
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@validate_request_json('first_name', 'last_name', 'email', 'password', 'role_name')
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return ResponseFormatter.error('User with this email already exists', status_code=400)
    
    # Get role
    role = Role.query.filter_by(name=data['role_name']).first()
    if not role:
        return ResponseFormatter.error('Invalid role', status_code=400)
    
    # Create new user
    user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone=data.get('phone'),
        role_id=role.id
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        return ResponseFormatter.success(
            data=user.to_dict(),
            message='User registered successfully',
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return ResponseFormatter.error(f'Error registering user: {str(e)}', status_code=500)


@auth_bp.route('/login', methods=['POST'])
@validate_request_json('email', 'password')
def login():
    """Login user"""
    data = request.get_json()
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return ResponseFormatter.error('Invalid email or password', status_code=401)
    
    if not user.is_active:
        return ResponseFormatter.error('User account is inactive', status_code=401)
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create access token
    access_token = create_access_token(identity=str(user.id))
    
    return ResponseFormatter.success(
        data={
            'access_token': access_token,
            'user': user.to_dict()
        },
        message='Login successful',
        status_code=200
    )


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current logged-in user"""
    return ResponseFormatter.success(data=current_user.to_dict())


@auth_bp.route('/change-password', methods=['POST'])
@token_required
@validate_request_json('old_password', 'new_password')
def change_password(current_user):
    """Change user password"""
    data = request.get_json()
    
    if not current_user.check_password(data['old_password']):
        return ResponseFormatter.error('Invalid current password', status_code=400)
    
    current_user.set_password(data['new_password'])
    db.session.commit()
    
    return ResponseFormatter.success(message='Password changed successfully')


@auth_bp.route('/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
    """Refresh access token"""
    access_token = create_access_token(identity=str(current_user.id))
    
    return ResponseFormatter.success(
        data={'access_token': access_token},
        message='Token refreshed successfully'
    )


# ============ PASSWORD RESET ============
@auth_bp.route('/forgot-password', methods=['POST'])
@validate_request_json('email')
def forgot_password():
    """Generate a password reset token and (in dev) return it in response or print it."""
    from datetime import datetime, timedelta
    import secrets

    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        # Do not reveal whether the email exists
        return ResponseFormatter.success(message='If an account with that email exists, a reset token has been sent')

    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires_at = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()

    # In production, send the token via email. For development return it in the response.
    return ResponseFormatter.success(data={'reset_token': token}, message='Password reset token generated')


@auth_bp.route('/reset-password', methods=['POST'])
@validate_request_json('token', 'new_password')
def reset_password():
    """Reset password using a valid token"""
    from datetime import datetime

    data = request.get_json()
    user = User.query.filter_by(reset_token=data['token']).first()
    if not user or not user.reset_token_expires_at or user.reset_token_expires_at < datetime.utcnow():
        return ResponseFormatter.error('Invalid or expired token', status_code=400)

    user.set_password(data['new_password'])
    user.reset_token = None
    user.reset_token_expires_at = None
    db.session.commit()

    return ResponseFormatter.success(message='Password has been reset successfully')
