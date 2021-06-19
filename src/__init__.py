import os
from flask import Flask, jsonify, request, Response
from flask_pymongo import PyMongo

from bson import json_util
from bson.objectid import ObjectId
from pymongo.collection import Collection, ReturnDocument

from .models.Usuario import Usuario
from .models.objectid import PydanticObjectId


app = Flask(__name__)
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.config['APPLICATION_ROOT'] = os.environ.get('BASE_URL')

def _url(path):
    return app.config['APPLICATION_ROOT'] + path

mongo = PyMongo(app)

users: Collection = mongo.db.usuarios


@app.route(_url('/api/'), methods=['GET'])
def index():
    return jsonify({'hello': 'world'})


@app.route(_url('/api/usuarios'), methods=['GET'])
def get_users():
    all_users = users.find()
    response = json_util.dumps(all_users)

    return Response(response, status=200, mimetype='application/json')


@app.route(_url('/api/usuarios/<string:username>'), methods=["GET", "PUT", "DELETE"])
def users_action(username):
    if request.method == 'GET':
        user_from_db = users.find({'nombre': username})
        if user_from_db.count() == 0:
            return Response(
                json_util.dumps({
                    'message': 'No existe el usuario en la base de datos',
                    'error': True}),
                status=400,
                mimetype='application/json')

        user = user_from_db[0]
        user = {
            'id': user['_id'],
            'nombre': user['nombre'],
            'correo': user['correo'],
        }
        return Response(
            json_util.dumps(user), status=200, mimetype='application/json')

    if request.method == 'DELETE':
        user_from_db = users.find({'nombre': username})
        if user_from_db.count() == 0:
            return Response(
                json_util.dumps({
                    'message': 'No existe el usuario en la base de datos',
                    'error': True}),
                status=400,
                mimetype='application/json')
        users.delete_one({'nombre': username})
        return Response(
            json_util.dumps({
                'message': 'Usuario borrado',
                'error': False}),
            status=200,
            mimetype='application/json')


@app.route(_url('/api/usuarios/login'), methods=['POST'])
def login():
    raw_user = request.get_json()
    user_exists = users.find({'nombre': raw_user['nombre']})

    if user_exists.count() == 0:
        return Response(
            json_util.dumps({
                'message': 'Nombre de usuario o contraseña incorrectos',
                'error': True}),
            status=400,
            mimetype='application/json')

    user_from_db = list(user_exists)[0]
    user = Usuario(**user_from_db)

    if user.check_password(raw_user['contraseña']):
        return Response(
            json_util.dumps({
                'message': 'Bienvenido {}'.format(raw_user['nombre']),
                'error': False}),
            status=200,
            mimetype='application/json')
    return Response(
        json_util.dumps({
            'message': 'Nombre de usuario o contraseña incorrectos',
            'error': True}),
        status=400,
        mimetype='application/json')


@app.route(_url('/api/usuario'), methods=["GET", "POST"])
def user():
    if request.method == 'POST':
        """Agrega un usuario a la base de datos.
        """
        raw_user = request.get_json()

        # Checa si el usuario llenó los campos requeridos
        if not all(k in raw_user and raw_user[k] != ''
                   for k in ('nombre', 'correo', 'contraseña')):
            return Response(
                json_util.dumps({
                    'message': 'Debes proveer nombre, correo y contraseña',
                    'error': True}),
                status=400,
                mimetype='application/json')

        user_exists = users.find(
            {'nombre': raw_user['nombre']}).count() > 0

        if user_exists:
            return Response(
                json_util.dumps({
                    'message': 'Este nombre ya está tomado, elige otro',
                    'error': True}),
                status=400,
                mimetype='application/json')

        user = Usuario(**raw_user)
        if not user.username_is_valid():

            return Response(
                json_util.dumps({
                    'message': 'El nombre de usuario no debe tener espacios'\
                        ' o caracteres especiales',
                    'error': True}),
                status=400,
                mimetype='application/json')

        user.create_hashed_password()
        insert_user = users.insert_one(user.to_bson())
        user.id = PydanticObjectId(str(insert_user.inserted_id))

        return Response(
            json_util.dumps({
                'message': 'Usuario creado',
                'error': False}),
            status=200,
            mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
