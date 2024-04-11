from functools import wraps
from flask import abort
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models import User, Permission, Role

def auth_required_with_permission(permission_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_user = get_jwt_identity()

            user = User.get_user_by_username(current_user)
            if not user:
                abort(401, 'Unauthorized')

            user_permissions = [p.system_name for r in user.roles for p in r.permissions]
            if permission_name not in user_permissions:
                abort(403, 'Forbidden')

            return func(*args, **kwargs)
        return wrapper
    return decorator

# Decorator for role based authorization
def role_required(role_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_user = get_jwt_identity()
            user = User.get_user_by_username(current_user)
            
            if not user:
                abort(401, 'Unauthorized')

            if role_name not in [r.role_name for r in user.roles]:
                abort(403, 'Forbidden')

            return fn(*args, **kwargs)
        return wrapper
    return decorator
