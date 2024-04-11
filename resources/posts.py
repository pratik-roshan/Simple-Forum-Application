from flask import request
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from db import db
from models import Post, Tag, User, Category

from decorators import auth_required_with_permission

blp = Blueprint('Post', __name__, url_prefix="/forum")

@blp.route('/posts', methods=['GET', 'POST'])
@jwt_required()
def posts():
    if request.method == 'GET':
        category_id = request.args.get('category_id')
        tag_names = request.args.getlist('tags')

        # Filter posts by category and tags if provided
        posts_query = Post.query

        if category_id:
            posts_query = posts_query.filter_by(category_id=category_id)

        if tag_names:
            posts_query = posts_query.join(Post.tags).filter(Tag.name.in_(tag_names))

        posts = posts_query.all()
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
@jwt_required()
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.view_count += 1
    db.session.commit()
    return {'post': post.serialize()}, 200

@blp.route('/posts/<int:post_id>', methods=['PUT'])
@auth_required_with_permission('edit_post')
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    data = request.json
    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    post.category_id = data.get('category_id', post.category_id)
    tag_names = data.get('tags', [])

    # CLEAR EXISTING TAGS
    existing_tags = post.tags.all()
    for tag in existing_tags:
        post.tags.remove(tag)

    for tag_name in tag_names:
        tag = Tag.query.filter_by(name=tag_name).first()
        if tag is None:
            tag = Tag(name=tag_name)
        post.tags.append(tag)
    
    db.session.commit()
    return {'message': 'Post updated successfully', 'post': post.serialize()}

@blp.route('/posts/<int:post_id>', methods=['DELETE'])
@auth_required_with_permission('delete_post')
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return {'message': 'Post deleted successfully'}

@blp.route('/posts/search', methods=['GET'])
@jwt_required()
def search_posts():
    search_query = request.args.get('q')

    if not search_query:
        return {'message': 'Search query is required'}, 400

    # Search posts by title or content
    posts = Post.query.filter(
        Post.title.ilike(f"%{search_query}%") | 
        Post.content.ilike(f"%{search_query}%")
    ).all()

    serialized_posts = [post.serialize() for post in posts]
    return {'posts': serialized_posts}, 200

@blp.route('/posts/like', methods=['POST'])
@jwt_required()
def like_post():
    data = request.get_json()
    post_id = data['post_id']
    current_username = get_jwt_identity()

    user = User.query.filter_by(username=current_username).first()
    post = Post.query.get(post_id)

    if user and post:
        if user not in post.liked_by:
            post.liked_by.append(user)
            post.likes += 1
            db.session.commit()
            return {'message': 'Post liked successfully'}, 200
        else:
            return {'message': 'You have already liked this post'}, 400
    else:
        return {'message': 'User or post not found'}, 404
    
@blp.route('/posts/unlike', methods=['POST'])
@jwt_required()
def unlike_post():
    data = request.get_json()
    post_id = data['post_id']
    current_username = get_jwt_identity()

    user = User.query.filter_by(username=current_username).first()
    post = Post.query.get_or_404(post_id)

    if user.id in [user.id for user in post.liked_by]:
        post.likes -= 1
        post.liked_by.remove(user)
        db.session.commit()
        return {'message': 'Post unliked successfully'}, 200
    
    else:
        return {'message': 'You have not liked this post yet'}, 400

