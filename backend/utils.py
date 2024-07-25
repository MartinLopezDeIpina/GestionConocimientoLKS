from flask import jsonify
from langchain_openai import OpenAIEmbeddings
from sqlalchemy import select, not_, exists
from sqlalchemy.orm import scoped_session, sessionmaker

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


# Dado un conjunto de nodos, devuelve un json con la estructura de árbol para el front
def get_nodos_json(nodos):
    node_ids = [node.nodoID for node in nodos]
    #Filtrar sólo las relaciones que tengan un ascendente en la lista de nodos
    relaciones = RelacionesNodo.query.filter(RelacionesNodo.descendente_id.in_(node_ids)).all()

    nodo_dict = {nodo.nodoID: nodo for nodo in nodos}

    json = {}
    add_node_to_json(json, nodos[0], relaciones, nodo_dict)

    return json


def add_node_to_json(json, nodo, relaciones, nodo_dict):
    relaciones_nodo = [relacion for relacion in relaciones if relacion.ascendente_id == nodo.nodoID]
    children = []
    for relacion in relaciones_nodo:
        descendente = nodo_dict[relacion.descendente_id]
        child = {}
        add_node_to_json(child, descendente, relaciones, nodo_dict)
        children.append(child)
    json['title'] = nodo.nombre
    json['id'] = nodo.nodoID
    if relaciones_nodo:
        json['children'] = children
        json['expanded'] = True
        json['isDirectory'] = True


def get_nodos_de_los_que_depende_nodo(nodo):
    if nodo.nodoID == get_root_node_id():
        return []

    relaciones = RelacionesNodo.query.filter_by(descendente_id=nodo.nodoID).all()
    relacion = relaciones[len(relaciones) - 1]
    nodos_dependencia = []

    nodo_dependencia = NodoArbol.query.filter_by(nodoID=relacion.ascendente_id).first()
    nodos_dependencia.append(nodo_dependencia)
    nodos_dependencia.extend(get_nodos_de_los_que_depende_nodo(nodo_dependencia))

    return nodos_dependencia


def get_nodos_descendientes_id(nodo_id):
    acumulador = []
    nodos_descendientes_id = get_nodos_descendientes_id_recursivo(nodo_id, acumulador)
    return nodos_descendientes_id


def get_nodos_descendientes_id_recursivo(nodo_id, acumulador):
    relaciones = RelacionesNodo.query.filter_by(ascendente_id=nodo_id).all()
    for relacion in relaciones:
        acumulador.append(relacion.descendente_id)
        get_nodos_descendientes_id_recursivo(relacion.descendente_id, acumulador)
    return acumulador


def create_user_personal_tree_from_json(json, email):
    node_ids = [node['id'] for node in json['ids']]

    nodos_conocimiento = []
    for node_id in node_ids:
        nodo = NodoArbol.query.filter_by(nodoID=node_id).first()
        nodos_conocimiento.append(nodo)

    nodo_conocimiento_completo = nodos_conocimiento.copy()
    #Añadir los nodos de los que dependen los nodos de conocimiento, el LLM no devuelve el árbol completo
    for nodo in nodos_conocimiento:
        nodos_dependencia = get_nodos_de_los_que_depende_nodo(nodo)
        for nodo_dependencia in nodos_dependencia:
            if nodo_dependencia not in nodo_conocimiento_completo:
                nodo_conocimiento_completo.append(nodo_dependencia)

    persist_user_personal_tree_db(nodo_conocimiento_completo, email)


def persist_user_personal_tree_db(nodos, email):
    conocimientos_usuario = ConocimientoUsuario.query.filter_by(usuario_email=email).all()
    for conocimiento_usuario in conocimientos_usuario:
        db.session.delete(conocimiento_usuario)
    db.session.commit()

    for nodo in nodos:
        conocimiento_usuario = ConocimientoUsuario(usuario_email=email, nodoID=nodo.nodoID, nivel_IA=0, nivel_validado=0)
        db.session.add(conocimiento_usuario)
    db.session.commit()


def get_user_personal_tree(email):
    conocimientos_usuario = ConocimientoUsuario.query.filter_by(usuario_email=email).all()
    conocimientos_usuario = [conocimiento.nodo for conocimiento in conocimientos_usuario]
    nodos_id = [conocimiento_usuario.nodoID for conocimiento_usuario in conocimientos_usuario]
    relaciones = RelacionesNodo.query.filter(RelacionesNodo.descendente_id.in_(nodos_id)).all()

    nodo_raiz_id = get_root_node_id()
    nodo_raiz = NodoArbol.query.filter_by(nodoID=nodo_raiz_id).first()

    json = {}
    json_tree = get_json_tree_from_unordered_nodes(nodo_raiz, conocimientos_usuario, relaciones, json)
    return json_tree


def get_json_tree_from_unordered_nodes(nodo, nodos, relaciones, json):
    nodo_dict = {nodo.nodoID: nodo for nodo in nodos}

    nodos_id = [nodo.nodoID for nodo in nodos]
    relaciones_nodo = [relacion for relacion in relaciones if relacion.ascendente_id == nodo.nodoID]

    children = []

    for relacion in relaciones_nodo:
        if relacion.descendente_id in nodos_id:
            descendente = nodo_dict[relacion.descendente_id]
            child = {}
            get_json_tree_from_unordered_nodes(descendente, nodos, relaciones, child)
            children.append(child)

    json['title'] = nodo.nombre
    json['id'] = nodo.nodoID
    if relaciones_nodo:
        json['children'] = children
        json['expanded'] = True
        json['isDirectory'] = True

    return json


def get_embedding(text):
    embeddings = OpenAIEmbeddings()
    embedded_text = embeddings.embed_query(text)
    return embedded_text


# Dado un texto, devuelve los nodos más cercanos en el espacio de embeddings
# Solo se devuelven los nodos hoja
# Por ejemplo, si queremos buscar frameworks backend, queremos que nos devuelva Django, Flask, etc.
def nodo_arbol_semantic_search(search_text):
    nodos = []

    search_embeddings = get_embedding(search_text)

    # Crear una sesión para hacer la consulta para poder llamarla desde threads concurrentes
    Session = scoped_session(sessionmaker(bind=db.engine))
    session = Session()
    try:
        result = session.scalars(select(NodoArbol)
                                 .where(not_(exists().where(NodoArbol.nodoID == RelacionesNodo.ascendente_id)))
                                 .order_by(NodoArbol.embedding.l2_distance(search_embeddings)).
                                 limit(10))
        result_ids = [nodo.nodoID for nodo in result]
    finally:
        Session.remove()

    for nodo_id in result_ids:
        nodos.append(NodoArbol.query.filter_by(nodoID=nodo_id).first())

    return nodos



