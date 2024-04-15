from flask import request, g
from flask_smorest import Blueprint
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import User
import re

jwt = JWTManager()
auth_bp = Blueprint('auth', __name__, url_prefix="/api/auth")

@auth_bp.post('/register')
def register_user():
    data = request.get_json()
    user = User.get_user_by_username(username=data.get('username'))
    if user:
        return {"message": "User already exists"}, 403
    
     # Check if the password is provided in the request data
    password = data.get('password')
    if not password:
        return {"message": "Password is required"}, 400
    
    # Validate the password format
    error_message = validate_password(password)
    if error_message:
        return {"message": error_message}, 400
    
    
    new_user = User(
        username = data.get('username'),
        email = data.get('email'),
        password=password
    )

    new_user.set_password(password=data.get('password'))

    new_user.save()

    return {"message": "User Registered Successfully"}, 201

def validate_password(password):
    if len(password) < 7:
        return "Password must be at least 7 characters long."

    # Check for at least one special character, one number, and one capital letter
    if not re.search(r'[!@#$%^&*()_+}{":?><,./;[\]]', password):
        return "Password must contain at least one special character."
    if not re.search(r'[0-9]', password):
        return "Password must contain at least one number."
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one capital letter."

    return None

@auth_bp.post('/login')
def login_user():
    data = request.get_json()
    user = User.get_user_by_username(username=data.get('username'))

    if user and (user.check_password(password=data.get('password'))):
        g.user = user
        access_token = create_access_token(identity=user.username)
        refresh_token = create_refresh_token(identity=user.username)
        
        return{
                "message": "Logged In Successfully",
                "tokens": {
                    "access": access_token,
                    "refresh": refresh_token
                    }
            }, 200
    
    return {"error": "Invalid username or password"}, 400

@auth_bp.get('/me')
@jwt_required()
def identity():
    current_user = get_jwt_identity()
    return {'message': f'Hello, {current_user}'}