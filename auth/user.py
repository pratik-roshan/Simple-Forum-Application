from flask import request
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required
from models import User
from schemas import UserSchema

user_bp = Blueprint('users', __name__, url_prefix="/users")

@user_bp.get('/all')
@jwt_required()
def get_all_users(): 
    users = User.query.all()
    result = UserSchema().dump(users, many=True)

    return {
        "users": result
    }, 200

@user_bp.get('/<string:username>')
@jwt_required()
def get_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    result = UserSchema().dump(user)

    return {
        "user": result
    }, 200