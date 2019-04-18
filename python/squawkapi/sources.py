import os
import wtforms_json
import requests
import feedparser
from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, Blueprint, request, jsonify
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
    for doc in db.sources.find({"_id": {"$in": user['sources']}}):
        obj = {
            "link": doc.get('link'),
            "host": doc.get('host'),
            "source_id": str(doc.get('_id')),
        }
        sources.append(obj)
    return jsonify({
            'sources': sources
            }), 200


@bp.route('/source/<id>/content', methods=['GET'])
@jwt_required
def get_source_content(id):
    db = mongo.db
    source = db.sources.find_one({'_id': ObjectId(id)})
    if source is not None:
        rss = requests.get(source.get('link'), headers={'User-Agent': 'SquawkAPI'})
        if rss.status_code == 200:
            d = feedparser.parse(rss.content)
            if d.bozo == 0:
                out = []
                for post in d.entries:
                    obj = {
                        "title": post.title,
                        "link": post.link,
                        "description": post.description,
                    }
                    out.append(obj)
                return jsonify({"status": "success",
                                "content": out}), 200
            else:
                return jsonify({"status": "failed",
                                "message": "Malformed RSS ressource.",
                                "bozo": str(d.bozo_exception)}), 422
        else:
            return jsonify({"status": "failed",
                            "message": "Could not retrieve source content."}), 422
    else:
        return jsonify({"status": "failed",
                        "message": "Cannot find source."}), 404

