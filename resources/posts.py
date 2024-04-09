from flask import Flask, request, jsonify
from flask_smorest import Blueprint
from db import db
from models import Post, Tag

blp = Blueprint('Post', __name__, url_prefix="/forum")

@blp.route('/posts', methods=['GET', 'POST'])
def posts():
    if request.method == 'GET':
        posts = Post.query.all()
        serialized_posts = [post.serialize() for post in posts]
        return {'posts': serialized_posts}, 200
    elif request.method == 'POST':
        data = request.json
        tag_names = data.get('tags', [])
        
        new_post = Post(title=data['title'], content=data['content'], category_id=data['category_id'])
        
        for tag_name in tag_names:
            tag = Tag.query. filter_by(name=tag_name).first()
            if tag is None:
                tag = Tag(name=tag_name)
            new_post.tags.append(tag)

        db.session.add(new_post)
        db.session.commit()
        return {'message': 'Post Created Successfully', 'post': new_post.serialize()}, 201

@blp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.view_count += 1
    db.session.commit()
    return {'post': post.serialize()}, 200

@blp.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    data = request.json
    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    post.category_id = data.get('category_id', post.category_id)
    tag_names = data.get('tags', [])
    for tag_name in tag_names:
        tag = Tag.query.filter_by(name=tag_name).first()
        if tag is None:
            tag = Tag(name=tag_name)
        post.tags.append(tag)
    
    db.session.commit()
    return {'message': 'Post updated successfully', 'post': post.serialize()}

@blp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return {'message': 'Post deleted successfully'}