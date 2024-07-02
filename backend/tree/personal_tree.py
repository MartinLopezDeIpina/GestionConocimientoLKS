from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

import utils
from LLM.LLMHandler import LLMHandler
from models import ConocimientoUsuario

personal_tree = Blueprint('personal_tree', __name__)


@personal_tree.route('/json_tree', methods=['GET'])
@jwt_required()
def personal_json_tree():
    user_email = get_jwt_identity()
    conocimientos_usuario = ConocimientoUsuario.query.filter_by(usuario_email=user_email).all()

    nodos = []
    for conocimiento in conocimientos_usuario:
        nodos.append(conocimiento.nodo)

    json = utils.get_nodos_json(nodos)
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
