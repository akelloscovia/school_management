from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User
from app import db


def token_required(fn):
    """Decorator to require valid JWT token"""
    @wraps(fn)
    def decorated(*args, **kwargs):
        # Allow CORS preflight requests to succeed without authentication
        if request.method == 'OPTIONS':
            return ('', 200)

        try:
            verify_jwt_in_request()
        except Exception as e:
            return {'success': False, 'error': str(e)}, 401

        current_user_id = get_jwt_identity()
        if isinstance(current_user_id, str) and current_user_id.isdigit():
            current_user_id = int(current_user_id)
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_active:
            return {'success': False, 'error': 'User not found or inactive'}, 401
        
        return fn(current_user, *args, **kwargs)
    return decorated


def role_required(*allowed_roles):
    """Decorator to require specific roles"""
    def decorator(fn):
        @wraps(fn)
        def decorated(current_user, *args, **kwargs):
            if current_user.role.name not in allowed_roles:
                return {'error': 'Insufficient permissions'}, 403
            return fn(current_user, *args, **kwargs)
        return decorated
    return decorator


def admin_required(fn):
    """Decorator to require admin role"""
    return role_required('admin')(fn)


def teacher_or_admin_required(fn):
    """Decorator to require teacher or admin role"""
    return role_required('teacher', 'admin')(fn)


def accountant_or_admin_required(fn):
    """Decorator to require accountant or admin role"""
    return role_required('accountant', 'admin')(fn)


def validate_request_json(*required_fields):
    """Decorator to validate JSON request body"""
    def decorator(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            if not request.is_json:
                return {'error': 'Request must be JSON'}, 400
            
            data = request.get_json()
            
            for field in required_fields:
                if field not in data or data[field] is None:
                    return {'error': f'Missing required field: {field}'}, 400
            
            return fn(*args, **kwargs)
        return decorated
    return decorator


def get_pagination_params():
    """Extract pagination parameters from request"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Limit per_page to prevent excessive queries
    if per_page > 100:
        per_page = 100
    if per_page < 1:
        per_page = 1
    if page < 1:
        page = 1
    
    return page, per_page


def paginate_query(query, page=1, per_page=20):
    """Paginate a query"""
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': [item.to_dict() for item in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
        'per_page': per_page
    }
