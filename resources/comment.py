from flask_smorest import Blueprint
from flask import request
from db import db
from models import Comment, Tag

blp = Blueprint('Comment', __name__, url_prefix="/forum")

@blp.route('/comments', methods=['GET', 'POST'])
def comments():
    if request.method == 'GET':
        comments = Comment.query.all()
        serialized_comments = []
        for comment in comments:
            serialized_comment = {
                'id': comment.id,
                'content': comment.content,
                'replies': [{'id': reply.id, 'content': reply.content} for reply in comment.replies]
            }
            serialized_comments.append(serialized_comment)
        return {'comments': serialized_comments}, 200
    
    elif request.method == 'POST':
        data = request.json
        content = data.get('content')
        post_id = data.get('post_id')
        parent_comment_id = data.get('parent_comment_id')

        new_comment = Comment(content=content, post_id=post_id, parent_comment_id=parent_comment_id)
        db.session.add(new_comment)
        db.session.commit()
        return {'message': 'Comment Created Successfully', 'comment': {'id': new_comment.id, 'content': new_comment.content}}, 201

@blp.route('/comments/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    data = request.json
    comment.content = data.get('content', comment.content)
    db.session.commit()
    return {'message': 'Comment updated successfully', 'comment': {'id': comment.id, 'content': comment.content}}

@blp.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return {'message': 'Comment deleted successfully'}
