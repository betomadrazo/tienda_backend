from flask import jsonify, request, Response, Blueprint
from flask_jwt_simple import (
    JWTManager, jwt_required, get_jwt_identity)
from bson import json_util
from bson.objectid import ObjectId

from .. import _url, users, articles
from ..models.Articulo import Articulo, get_image_name, convert_base64_to_image
from ..models.objectid import PydanticObjectId

from .. import app, mongo, _url

articulos_api = Blueprint('articulos_api', __name__)


@articulos_api.route(_url('/api/articulos'),
                     methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required
def articles_actions():
    # Create a new article
    if request.method == 'GET':
        all_articles = articles.find()
        response = json_util.dumps(all_articles)

        return Response(response, status=200, mimetype='application/json')

    if request.method == 'POST':
        # Create an article; this article will belong to the user
        user_id = ObjectId(get_jwt_identity())
        raw_article = request.get_json()

        user_exists = users.find({'_id': user_id}).count() > 0
        if not user_exists:
            return Response(
                json_util.dumps({
                    'message': 'El usuario no existe'
                }),
                status=400,
                mimetype='application/json')

        raw_article['idUsuario'] = user_id
        article = Articulo(**raw_article)

        image_name = get_image_name(article.nombre)
        article.imagen = convert_base64_to_image(
            request.url_root, article.imagen, image_name)

        # article.convert_base64_to_image(request.url_root)
        insert_article = articles.insert_one(article.to_json())
        article.id = PydanticObjectId(str(insert_article.inserted_id))

        return Response(
            json_util.dumps({
                'message': 'Artículo creado',
                'id': article.id,
                'nombre': article.nombre,
                'imagen': article.imagen,
                'precio': article.precio,
                'descripcion': article.descripcion
            }),
            status=201,
            mimetype='application/json')


@articulos_api.route(_url('/api/articulos/<string:article_id>'),
                     methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def article_actions(article_id):
    # Checa si el id es válido
    try:
        article = articles.find({'_id': ObjectId(article_id)})
    except Exception as e:
        return Response(
            json_util.dumps({
            'message': 'El id del artículo no es válido'
        }), status=400, mimetype='application/json')
    user_id = get_jwt_identity()
    if article.count() == 0:
        return Response(json_util.dumps({
            'message': 'El artículo no existe en la base de datos'
        }), status=400, mimetype='application/json')

    raw_article = request.get_json()
    article = article[0]

    if request.method == 'GET':
        return Response(
            json_util.dumps(article), status=200, mimetype='application/json')

    if user_id != article['idUsuario']:
        # sólo el creador del artículo lo puede modificar
        return Response(
            json_util.dumps({
                'message': 'No estás autorizado para modificar el artículo'
            }),
            status=401,
            mimetype='application/json')

    if request.method == 'PUT':
        # Sólo actualizar los campos que ya tiene el producto(excepto ids)
        updatable_items = {
            k: v for (k, v) in raw_article.items()
            if k in ('nombre', 'imagen', 'precio', 'descripcion')}

        # Si hay imagen para actualizar, convertirla en archivo
        if 'imagen' in updatable_items:
            image_name = get_image_name(user_id)
            updatable_items['imagen'] = convert_base64_to_image(
            request.url_root, updatable_items['imagen'], image_name)


        update_article = articles.update_one(
            {'_id': ObjectId(article_id)}, {'$set': updatable_items})

        if update_article.modified_count == 1:
            return Response(
                json_util.dumps({
                    'message': 'Articulo modificado'
                }),
                status=200,
                mimetype='application/json'
            )
        return Response(
            json_util.dumps({
                'message': 'No se pudo actualizar el artículo'
            }),
            status=500,
            mimetype='application/json'
        )

    if request.method == 'DELETE':
        try:
            articles.delete_one({'_id': ObjectId(article_id)})
            return Response(
                json_util.dumps({
                    'message': 'Articulo eliminado'
                }),
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            return Response(
                json_util.dumps({
                    'message': 'No se pudo eliminar el artículo'
                }),
                status=500,
                mimetype='application/json'
            )


@articulos_api.route(_url('/api/articulos/usuario/<string:user_id>'),
                    methods=['GET'])
def user_articles(user_id):
    try:
        user_articles = articles.find({'idUsuario': user_id})
        return Response(
            json_util.dumps(user_articles),
            status=200,
            mimetype='application/json')
    except Exception as e:
        return Response(
            json_util.dumps({
            'message': 'El id del usuario no es válido'
        }), status=400, mimetype='application/json')
