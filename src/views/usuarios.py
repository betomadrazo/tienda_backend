from flask import Flask, jsonify, request, Response, Blueprint

from flask_jwt_simple import (
    JWTManager, jwt_required, create_jwt, get_jwt_identity)
from bson import json_util
from bson.objectid import ObjectId
from pymongo.collection import Collection, ReturnDocument

from .. import _url, users
from ..models.Usuario import Usuario
from ..models.objectid import PydanticObjectId

usuarios_api = Blueprint('usuarios_api', __name__)


@usuarios_api.route(_url('/api/usuarios'), methods=['GET'])
# @jwt_required
def get_users():
    all_users = users.find()
    response = json_util.dumps(all_users)

    return Response(response, status=200, mimetype='application/json')


@usuarios_api.route(_url('/api/autenticar'), methods=['POST'])
def auth_user():
    return Response(
        json_util.dumps({
            'message': 'Hola.'}),
        status=200,
        mimetype='application/json')
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

        jwt_token = create_jwt(identity=str(user.id))

        return Response(
            json_util.dumps({
                'message': 'Bienvenido {}'.format(raw_user['nombre']),
                'id': user.id,
                'nombre': user.nombre,
                'correo': user.correo,
                'error': False,
                'jwt_token': jwt_token}),

            status=200,
            mimetype='application/json')
    return Response(
        json_util.dumps({
            'message': 'Nombre de usuario o contraseña incorrectos',
            'error': True}),
        status=400,
        mimetype='application/json')


@usuarios_api.route(_url('/api/usuario'), methods=["GET", "POST"])
def user():
    if request.method == 'POST':
        """Agrega un usuario a la base de datos.
        """
        raw_user = request.get_json()

        # Checa si el usuario no llenó los campos requeridos
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
                    'message': 'El nombre de usuario no debe tener espacios'
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
                'id': user.id,
                'nombre': user.nombre,
                'correo': user.correo,
                'error': False}),
            status=201,
            mimetype='application/json')


@usuarios_api.route(_url('/api/usuarios/<string:username>'),
                    methods=["GET", "PUT", "DELETE"])
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
