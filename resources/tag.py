from flask import request
from flask_smorest import Blueprint
from db import db
from models import Tag

blp = Blueprint('Tag', __name__, url_prefix="/forum")

@blp.route('/tags', methods=['GET', 'POST'])
def tags():
    if request.method == 'GET':
        tags = Tag.query.all()
        serialized_tags = [{'id': tag.id, 'name': tag.name} for tag in tags]
        return {'tags': serialized_tags}, 200
    
    elif request.method == 'POST':
        data = request.json
        tag_name = data.get('name')

        existing_tag = Tag.query.filter_by(name=tag_name).first()
        if existing_tag:
            return {'message': 'Tag with this name already exists'}, 400

        new_tag = Tag(name=tag_name)
        db.session.add(new_tag)
        db.session.commit()
        return {'message': 'Tag Created Successfully', 'tag': {'id': new_tag.id, 'name': new_tag.name}}, 201

@blp.route('/tags/<int:tag_id>', methods=['PUT'])
def update_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    data = request.json
    tag.name = data.get('name', tag.name)
    db.session.commit()
    return {'message': 'Tag updated successfully', 'tag': {'id': tag.id, 'name': tag.name}}

@blp.route('/tags/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return {'message': 'Tag deleted successfully'}
