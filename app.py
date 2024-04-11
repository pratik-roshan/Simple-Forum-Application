from flask import Flask
from flask_smorest import Api
from flask_migrate import Migrate

from dotenv import load_dotenv
import os

from db import db
import models

from resources.posts import blp as PostBlueprint
from resources.category import blp as CategoryBlueprint
from resources.comment import blp as CommentBlueprint
from resources.tag import blp as TagBlueprint

from auth import auth_bp, jwt, user_bp, user_management_bp

def create_app():
    app = Flask(__name__)

    load_dotenv()

    db_user = os.getenv('DB_USER')
    db_pwd = os.getenv('DB_PWD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')

    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_TIME'] = os.environ.get('JWT_ACCESS_TOKEN_EXPIRES')
    app.config['JWT_REFRESH_TOKEN_TIME'] = os.environ.get('JWT_REFRESH_TOKEN_EXPIRES')
    
    db.init_app(app)
    migrate = Migrate(app, db)
    
    with app.app_context():
        db.create_all()

    jwt.init_app(app)
    
    app.register_blueprint(PostBlueprint)
    app.register_blueprint(CategoryBlueprint)
    app.register_blueprint(CommentBlueprint)
    app.register_blueprint(TagBlueprint)

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(user_management_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)