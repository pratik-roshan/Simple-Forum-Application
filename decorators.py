from functools import wraps
from flask import g, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from models import User

def auth_required_with_permission(permission):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_user = get_jwt_identity()

            user = User.get_user_by_username(current_user)
            if not user:
                abort(401, 'Unauthorized')

            user_permissions = [p.permission_name for r in user.roles for p in r.permissions]
            if not any(permission in user_permissions for permission in permission):
                abort(403, 'Forbidden')
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Decorator for role based authorization
def role_required(role):
    def decorator(fn):
        
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            if current_user.get('role') != role:
                return {'message': 'Insufficient permissions'}, 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator