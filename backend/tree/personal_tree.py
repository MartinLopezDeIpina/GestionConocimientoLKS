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
    todos_nodos = NodoArbol.query.all()

    tree = utils.get_nodos_json(todos_nodos)
    personal_tree = utils.get_user_personal_tree(user_email)
    nodos_id = [nodo.nodoID for nodo in ConocimientoUsuario.query.filter_by(usuario_email=user_email).all()]

    return jsonify({"tree": [tree], "personal_tree": [personal_tree], "personal_nodes_id": [nodos_id]})


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


@personal_tree.route('/personal_nodes_id')
@jwt_required()
def personal_nodes_id():
    email = get_jwt_identity()
    conocimientos_usuario = ConocimientoUsuario.query.filter_by(usuario_email=email).all()
    nodos_id = [conocimiento_usuario.nodoID for conocimiento_usuario in conocimientos_usuario]
    return jsonify(nodos_id), 200


@personal_tree.route('/add_node/<nombre>/<int:nodo_id>', methods=['POST'])
@jwt_required()
def add_node(nombre, nodo_id):
    email = get_jwt_identity()
    nodo = NodoArbol.query.get(nodo_id)

    if nodo is None:
        return Response('nodo no existe', status=400)

    nodos_dependientes = utils.get_nodos_de_los_que_depende_nodo(nodo)

    for nodo_dependiente in nodos_dependientes:
        conocimiento = ConocimientoUsuario.query.filter_by(usuario_email=email, nodoID=nodo_dependiente.nodoID).first()
        if conocimiento is None:
            db.session.add(ConocimientoUsuario(usuario_email=email, nodoID=nodo_dependiente.nodoID, nivel_IA=0, nivel_validado=0))
    db.session.add(ConocimientoUsuario(usuario_email=email, nodoID=nodo_id, nivel_IA=0, nivel_validado=0))
    db.session.commit()

    nodos_dependientes_id = [nodo_dependiente.nodoID for nodo_dependiente in nodos_dependientes]
    nodos_dependientes_id.append(nodo_id)

    return jsonify(message='Nodo agregado', status=200, nodos_dependientes=[nodos_dependientes_id])
