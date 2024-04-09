from flask import request
from flask_smorest import Blueprint
from models import User, Role, Permission
from db import db

from flask_jwt_extended import jwt_required
from decorators import auth_required_with_permission

user_management_bp = Blueprint('user_management', __name__)

@user_management_bp.route('/create_role', methods=['POST'])
@auth_required_with_permission('create')
def create_role():
    data = request.get_json()
    role_name = data.get('role_name')

    role_exists = Role.query.filter_by(role_name=role_name).first()

    if role_exists:
        return{"error": "Role already exists"}, 400

    role = Role(role_name=role_name)
    db.session.add(role)
    db.session.commit()

    return {"message": "Role created successfully"}, 201

@user_management_bp.route('/create_permission', methods=['POST'])
@auth_required_with_permission('create')
def create_permission():
    data = request.get_json()
    system_name = data.get('system_name')
    display_name = data.get('display_name')
    
    existing_permission = Permission.query.filter_by(display_name=display_name).first()
    
    if existing_permission:
        return {"error": "Permission already exists"}, 400

    permission = Permission(system_name=system_name, display_name=display_name)

    db.session.add(permission)
    db.session.commit()

    return {"message": "Permission created successfully"}

@user_management_bp.route('/assign_role', methods=['POST'])
def assign_role():
    data = request.get_json()
    username = data.get('username')
    role_name = data.get('role_name')

    user = User.get_user_by_username(username)
    role = Role.query.filter_by(role_name=role_name).first()

    if not role:
        return {"error": "Role does not exist"}, 404

    if user:
        if role in user.roles:
            return{"message": "Role already assigned to user"}, 200
        
        user.roles.append(role)
        db.session.commit()
        return {"message": "Role assigned to user successfully"}, 200
    
    else:
        return {"error": "User not found"}, 404

@user_management_bp.route('/assign_permission', methods=['POST'])
def assign_permission():
    data = request.get_json()
    role_name = data.get('role_name')
    permission_name = data.get('permission_name')

    role = Role.query.filter_by(role_name=role_name).first()
    permission = Permission.query.filter_by(display_name=permission_name).first()

    if not role:
        if not permission:
            return {"error": "Role and Permission does not exist"}, 404

    if not permission:
        return {"error": "Permission does not exist"}, 404

    if role:
        if permission in role.permissions:
            return {"message": "Permission already assigned to Role"}, 200
        
        role.permissions.append(permission)
        db.session.commit()
        return {"message": "Permission assigned to role successfully"}, 200
    
    else:
        return {"error": "Role does not exist"}, 404
