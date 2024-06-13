from flask import jsonify

from models import NodoArbol, RelacionesNodo


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
