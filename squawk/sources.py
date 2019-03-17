import os

import wtforms_json
from dotenv import load_dotenv
from flask import Flask, Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pymongo import PyMongo
from wtforms import Form, StringField, validators


load_dotenv()
app = Flask(__name__)
bp = Blueprint('sources', __name__, url_prefix='')
wtforms_json.init()
mongo = PyMongo(app, os.getenv('MONGO_URI'))


class SourceForm(Form):
    link = StringField('Link', [validators.Length(min=4, max=100)])
    name = StringField('Name', [validators.Length(min=6, max=35)])


@bp.route('/source', methods=['POST'])
@jwt_required
def create_source():
    db = mongo.db
    form = SourceForm.from_json(request.get_json())
    if form.validate():
        username = get_jwt_identity()
        user = db.users.find_one({'username': username})
        if user is not None:
            source = {
                "link": form.link.data,
                "host": form.name.data,
            }
            source = db.sources.insert_one(source)
            db.users.update_one({"username": username}, {'$push': {'sources': source.inserted_id}})
            return jsonify({"status": "success",
                            "source_id": str(source.inserted_id)}), 201
        else:
            return jsonify({"status": "failed",
                            "message": "Bad token."}), 401
    else:
        return jsonify({"status": "failed",
                        "message": "Invalid supplied data."}), 400


@bp.route('/sources', methods=['GET'])
@jwt_required
def get_user_sources():
    db = mongo.db
    username = get_jwt_identity()
    user = db.users.find_one({'username': username})
    sources = []
    for doc in db.sources.find({"_id": { "$in": user['sources']}} ):
        doc.pop('_id')
        obj = {
            "link": doc.get('link'),
            "host": doc.get('host'),
        }
        sources.append(obj)
    return jsonify({
            'sources': sources
            }), 200
