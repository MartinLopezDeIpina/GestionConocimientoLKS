from flask import jsonify

from database import db
from models import NodoArbol, RelacionesNodo, Usuario, ConocimientoUsuario


def llm_json_tree():
    nodos = NodoArbol.query.all()
    relaciones = RelacionesNodo.query.all()
    nodo_dict = {nodo.nodoID: nodo for nodo in nodos}

    json = {}
    add_node_to_json_llm_format(json, nodos[0], relaciones, nodo_dict)

    return jsonify(json)


def add_node_to_json_llm_format(json, nodo, relaciones, nodo_dict):
    relaciones_nodo = [relacion for relacion in relaciones if relacion.ascendente_id == nodo.nodoID]
    children = []
    for relacion in relaciones_nodo:
        descendente = nodo_dict[relacion.descendente_id]
        child = {}
        add_node_to_json_llm_format(child, descendente, relaciones, nodo_dict)
        children.append(child)
    json["skill"] = nodo.nombre
    json["id"] = nodo.nodoID
    if relaciones_nodo:
        json["sub_skill"] = children


def read_data_from_file(file):
    with open(file, 'r', encoding='utf-8') as f:
        return f.read()


def count_parents_of_leafs():
    nodos = NodoArbol.query.all()
    relaciones = RelacionesNodo.query.all()
    nodo_dict = {nodo.nodoID: nodo for nodo in nodos}
    parents_list = set()

    leafs = [nodo for nodo in nodos if not [relacion for relacion in relaciones if relacion.ascendente_id == nodo.nodoID]]
    for leaf in leafs:
        for relacion in relaciones:
            if relacion.descendente_id == leaf.nodoID:
                parent = nodo_dict[relacion.ascendente_id]
                parents_list.add(parent)

    return len(parents_list)


def create_user_if_not_exists(email, name):
    user = Usuario.query.filter_by(email=email).first()
    if not user:
        user = Usuario(email=email, nombre=name)
        create_user_personal_tree(email=email)
        db.session.add(user)
        db.session.commit()


def create_user_personal_tree(email):
    if ConocimientoUsuario.query.filter_by(usuario_email=email).first() is None:
        db.session.add(ConocimientoUsuario(usuario_email=email, nodoID=get_root_node_id(),
                                           nivel_IA=0, nivel_validado=0))


def get_root_node_id():
    return NodoArbol.query.order_by(NodoArbol.nodoID).first().nodoID


