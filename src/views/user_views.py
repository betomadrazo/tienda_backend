import os
from flask import Flask, jsonify, request, Response
from flask_pymongo import PyMongo

from bson import json_util
from bson.objectid import ObjectId
from pymongo.collection import Collection, ReturnDocument

from ..models.Usuario import Usuario
from ..models.objectid import PydanticObjectId

from src import mongo
from src import users

from flask_cors import CORS

import src.views.user_views as user_views


def index():
    return jsonify({'hello': 'world'})


def get_users():
    all_users = users.find()
    response = json_util.dumps(all_users)

    return Response(response, status=200, mimetype='application/json')