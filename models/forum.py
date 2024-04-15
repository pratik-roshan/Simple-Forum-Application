from db import db
from models.users import User

post_tag = db.Table('post_tag',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

post_likes = db.Table(
    'post_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    view_count = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    likes = db.Column(db.Integer, default=0)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    category = db.relationship('Category', backref=db.backref('posts', lazy=True))
    tags = db.relationship('Tag', secondary=post_tag, back_populates='posts', lazy='dynamic', cascade='all, delete')
    creator = db.relationship('User', backref='created_posts', foreign_keys=[creator_id])
    liked_by = db.relationship('User', secondary=post_likes, backref='liked_posts')

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'view_count': self.view_count,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'tags': [tag.name for tag in self.tags],
            'creator': self.creator.username if self.creator else None,
            'likes': self.likes,
            'liked_by': [user.username for user in self.liked_by]
        }

class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    parent_comment = db.relationship('Comment', remote_side=[id], backref=db.backref('replies', lazy=True, cascade='all, delete'))
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    posts = db.relationship('Post', secondary=post_tag, back_populates='tags', lazy='dynamic')