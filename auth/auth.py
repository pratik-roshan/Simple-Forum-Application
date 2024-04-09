from flask import request, g
from flask_smorest import Blueprint
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import User

jwt = JWTManager()
auth_bp = Blueprint('auth', __name__, url_prefix="/auth")

@auth_bp.post('/register')
def register_user():
    data = request.get_json()
    user = User.get_user_by_username(username=data.get('username'))
    if user:
        return {"message": "User already exists"}, 403
    
    new_user = User(
        username = data.get('username'),
        email = data.get('email')
    )

    new_user.set_password(password=data.get('password'))

    new_user.save()

    return {"message": "User Registered Successfully"}, 201

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

@auth_bp.get('/identity')
@jwt_required()
def identity():
    current_user = get_jwt_identity()
    return {'message': f'Hello, {current_user}'}