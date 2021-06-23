import os
from flask import Flask, jsonify, request, Response
from flask_pymongo import PyMongo

from bson import json_util
from bson.objectid import ObjectId
from pymongo.collection import Collection, ReturnDocument

from flask_jwt_simple import (
    JWTManager, jwt_required, create_jwt, get_jwt_identity)

from flask_cors import CORS

app = Flask(__name__)
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.config['APPLICATION_ROOT'] = os.environ.get('BASE_URL')

app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')

app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

jwt = JWTManager(app)


def _url(path):
    return app.config['APPLICATION_ROOT'] + path

mongo = PyMongo(app)

users: Collection = mongo.db.usuarios
articles: Collection = mongo.db.articulos

from .views.articulos import articulos_api
from .views.usuarios import usuarios_api

app.register_blueprint(articulos_api)
app.register_blueprint(usuarios_api)


@app.route(_url('/api/'), methods=['GET'])
def say_hi():
    return Response(
        json_util.dumps({
            'message': 'Hola.'}),
        status=200,
        mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
