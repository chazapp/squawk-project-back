import functools
import os

from dotenv import load_dotenv
from flask import (
    Blueprint, jsonify, request, g,
    Flask)
from flask_pymongo import PyMongo
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from flask_jwt_extended import create_access_token

import wtforms_json
from pymongo import MongoClient

load_dotenv()
app = Flask(__name__)
bp = Blueprint('auth', __name__, url_prefix='')
wtforms_json.init()
mongo = PyMongo(app, os.getenv('MONGO_URI'))


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [validators.Length(min=5, max=15)])


class LoginForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [validators.Length(min=5, max=15)])


@bp.route('/register', methods=(['POST']))
def register():
    db = mongo.db
    form = RegistrationForm.from_json(request.get_json())
    if form.validate():
        user = db.users.find_one({'email': form.email.data})
        if user is not None:
            return jsonify({"status": "failed",
                            "message": "User already exists."}), 409
        user = {
            "username": form.username.data,
            "email": form.email.data,
            "password": generate_password_hash(form.password.data, salt_length=8),
            "accessTokens": [],
            "sources": [],
        }
        db.users.insert_one(user)
        access_token = create_access_token(identity=user['username'])
        db.users.update_one({'email': user['email']}, {'$push': {'accessTokens': access_token}})
        return jsonify({"status": "success",
                        "token": access_token}), 200
    return jsonify({"status": "failed",
                    "message": "Invalid supplied data."}), 400


@bp.route('/auth', methods=(['POST']))
def authenticate():
    form = LoginForm.from_json(request.get_json())
    db = mongo.db
    if form.validate():
        user = db.users.find_one({'email': form.email.data})
        if user is not None:
            if check_password_hash(user['password'], form.password.data):
                access_token = create_access_token(identity=user['username'])
                db.users.update_one({'email': user['email']}, {'$push': {'accessTokens': access_token}})
                return jsonify({"status:": "success",
                                "token": access_token}), 200
            else:
                return jsonify({"status": "failed",
                                "message": "Bad password."}), 400
        else:
            return jsonify({"status": "failed",
                            "message": "Email not found."}), 404
    else:
        return jsonify({"status": "failed",
                        "message": "Invalid supplied data."}), 400

