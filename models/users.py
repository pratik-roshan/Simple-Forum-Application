from db import db
from werkzeug.security import generate_password_hash, check_password_hash

user_role_association = db.Table(
    'user_role_association',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'))
)

role_permission_association = db.Table(
    'role_permission_association',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id', ondelete='CASCADE')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id', ondelete='CASCADE'))
)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)

    authored_posts = db.relationship('Post', backref='author', lazy='dynamic')
    roles = db.relationship('Role', secondary=user_role_association, backref=db.backref('users', lazy='dynamic', cascade='all, delete'))

    def __repr__(self):
        return '<User %r>' % self.username
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    @classmethod
    def get_user_by_username(cls, username):
        return cls.query.filter_by(username=username).first()
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(), unique=True, nullable=False)
    permissions = db.relationship('Permission', secondary=role_permission_association, backref=db.backref('roles', lazy='dynamic', cascade='all, delete'))

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    system_name = db.Column(db.String(), unique=True, nullable=False)
    display_name = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return '<Permission %r>' % self.display_name
