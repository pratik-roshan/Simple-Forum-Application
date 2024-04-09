from flask import request
from flask_smorest import Blueprint
from db import db
from models import Category

blp = Blueprint('Category', __name__, url_prefix="/forum")

@blp.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'GET':
        categories = Category.query.all()
        serialized_categories = [{'id': cat.id, 'name': cat.name} for cat in categories]
        return {'categories': serialized_categories}, 200
    elif request.method == 'POST':
        data = request.json
        category_name = data.get('name')
        existing_category = Category.query.filter_by(name=category_name).first()
        if existing_category:
            return {'message': 'Category with this name already exists'}, 400
        new_category = Category(name=category_name)
        db.session.add(new_category)
        db.session.commit()
        return {'message': 'Category Created Successfully', 'category': {'id': new_category.id, 'name': new_category.name}}, 201

@blp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = Category.query.get_or_404(category_id)
    return {'category': {'id': category.id, 'name': category.name}}, 200

@blp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.json
    category.name = data.get('name', category.name)
    db.session.commit()
    return {'message': 'Category updated successfully', 'category': {'id': category.id, 'name': category.name}}

@blp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return {'message': 'Category deleted successfully'}
