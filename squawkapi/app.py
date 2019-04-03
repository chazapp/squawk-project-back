from flask import Flask, g
from flask_jwt_extended import JWTManager

from squawkapi.auth import bp as auth
from squawkapi.sources import bp as sources
import os
from dotenv import load_dotenv


def create_app(testing=False):
    app = Flask(__name__, instance_relative_config=True)
    if not testing:
        load_dotenv()
        app.config.from_mapping(
            SECRET_KEY=os.getenv('SECRET'),
            JWT_SECRET_KEY=os.getenv('SECRET'),
            MONGO_URI=os.getenv('MONGO_URI')
        )
    else:
        app.config.from_mapping(
            TESTING=True,
            JWT_SECRET_KEY="SECRET",
            MONGO_URI='mongodb://localhost:27017/squawkTest'
        )
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    jwt = JWTManager(app)
    app.register_blueprint(auth)
    app.register_blueprint(sources)
    return app
