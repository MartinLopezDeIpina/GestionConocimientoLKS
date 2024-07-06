from flask import Blueprint, request, Response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

import utils
from LLM.LLMHandler import LLMHandler
from database import db
from models import ConocimientoUsuario, NodoArbol

personal_tree = Blueprint('personal_tree', __name__)


@personal_tree.route('/json_tree', methods=['GET'])
@jwt_required()
def personal_json_tree():
    user_email = get_jwt_identity()
    json = utils.get_user_personal_tree(user_email)
    return [json]


@personal_tree.route('/upload_tree_from_cv', methods=['POST'])
@jwt_required()
def personal_upload_tree_from_cv():
    user_cv = request.get_json().get('cv')
    email = get_jwt_identity()

    knowledge_json = LLMHandler().handle_knowledges(user_cv)

    utils.create_user_personal_tree_from_json(knowledge_json, email)
    return {'message': 'Árbol subido correctamente', 'status': 200}


@personal_tree.route('/upload_tree', methods=['post'])
@jwt_required()
def personal_upload_tree():
    user_email = get_jwt_identity()
    arbol_json = request.get_json().get('arbol')


@personal_tree.route('/delete_node/<int:nodo_id>', methods=['GET', 'DELETE'])
@jwt_required()
def delete_node(nodo_id):
    email = get_jwt_identity()
    nodo = ConocimientoUsuario.query.filter_by(nodoID=nodo_id, usuario_email=email).first()
    if nodo is None:
        return Response('Nodo no existe', status=400)

    delete_node_from_user(nodo, email)

    return jsonify({'message':'Nodo eliminado', 'status':200})


def delete_node_from_user(nodo_conocimiento_personal, email):
    if nodo_conocimiento_personal is not None:
        db.session.delete(nodo_conocimiento_personal)
        delete_nodos_descendientes_arbol_personal(nodo_conocimiento_personal.nodoID, email)
        db.session.commit()


def delete_nodos_descendientes_arbol_personal(nodo_id, email):
    nodos_descendientes_id = utils.get_nodos_descendientes_id(nodo_id)
    ConocimientoUsuario.query.filter(ConocimientoUsuario.nodoID.in_(nodos_descendientes_id), ConocimientoUsuario.usuario_email == email).delete()


@personal_tree.route('/json_tree/<int:parent_node_id>')
def json_tree_from_parent(parent_node_id):
    nodos_id = utils.get_nodos_descendientes_id(parent_node_id)
    nodos_id.append(parent_node_id)

    nodos = NodoArbol.query.filter(NodoArbol.nodoID.in_(nodos_id)).all()

    json = utils.get_nodos_json(nodos)
    return [json]
