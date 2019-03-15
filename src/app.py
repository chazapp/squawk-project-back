import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from src.auth import bp as auth


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET'),
        JWT_SECRET_KEY=os.getenv('SECRET'),
        MONGO_URI=os.getenv('MONGO_URI')
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    return app


if __name__ == '__main__':
    load_dotenv()
    app = create_app()
    jwt = JWTManager(app)
    app.register_blueprint(auth)
    app.run(debug=True)
