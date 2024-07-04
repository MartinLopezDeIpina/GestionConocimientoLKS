import csv
import os
from itertools import islice

from flask import Response, jsonify, request, Flask
from flask_jwt_extended import jwt_required, get_jwt_identity
from treelib import Tree

import utils
from database import db
from models import NodoArbol, RelacionesNodo, ConocimientoUsuario

from config import Config

app = Flask(__name__)


def init_routes(app):

    @app.route('/eliminarBD')
    def eliminarBD():
        db.drop_all()
        return 'Base de datos eliminada'

    @app.route('/api/add_csv')
    def store_tree_from_csv():
        file_path = os.path.join(app.static_folder, 'conocimientosLKS.csv')

        # Keep track of the last node at each depth level
        last_node_at_depth = {}

        nodoRaiz = NodoArbol.query.filter_by(nombre='LKS').first()

        if nodoRaiz is None:
            nodoRaiz = NodoArbol(nombre='LKS')
            db.session.add(nodoRaiz)
            db.session.commit()

        last_node_at_depth[0] = nodoRaiz

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in islice(reader, 3, None):
                # Iterate over each cell in the row
                for i in range(len(row)):
                    node = row[i]

                    # Skip empty cells
                    if not node:
                        continue

                    parent = last_node_at_depth.get(i-1)

                    nodo = NodoArbol(nombre=node)
                    #nodo = NodoArbol.query.order_by(-NodoArbol.nombre).first()
                    db.session.add(nodo)
                    db.session.commit()

                    if parent is None:
                        relacion = RelacionesNodo(ascendente_id=nodoRaiz.nodoID, descendente_id=nodo.nodoID)
                    else:
                        relacion = RelacionesNodo(ascendente_id=parent.nodoID, descendente_id=nodo.nodoID)

                    db.session.add(relacion)
                    db.session.commit()

                    # Update the last node at the current depth level
                    last_node_at_depth[i] = nodo

    @app.route('/api/delete')
    def delete_tree():
        nodos = NodoArbol.query.all()
        relaciones = RelacionesNodo.query.all()

        for relacion in relaciones:
            db.session.delete(relacion)

        for nodo in nodos:
            db.session.delete(nodo)

        db.session.commit()
        return 'Tree deleted'

    @app.route('/api/tree')
    def print_tree():
        nodos = NodoArbol.query.all()
        relaciones = RelacionesNodo.query.all()

        nodo_dict = {nodo.nodoID: nodo for nodo in nodos}

        tree = Tree()

        tree.create_node(nodos[0].nombre, nodos[0].nodoID)

        add_node_to_tree(tree, nodos[0], relaciones, nodo_dict)

        print(tree.show(stdout=False, sorting=False))
        tree_str = tree.show(stdout=False, sorting=False)
        return '<pre>' + tree_str + '</pre>'

    def add_node_to_tree(tree, nodo, relaciones, nodo_dict):
        relaciones_nodo = [relacion for relacion in relaciones if relacion.ascendente_id == nodo.nodoID]
        for relacion in relaciones_nodo:
            descendente = nodo_dict[relacion.descendente_id]
            tree.create_node(descendente.nombre, descendente.nodoID, parent=nodo.nodoID)
            add_node_to_tree(tree, descendente, relaciones, nodo_dict)

    @app.route('/api/json_tree')
    def json_tree():
        nodos = NodoArbol.query.all()

        json = utils.get_nodos_json(nodos)
        return [json]

    @app.route('/api/get_llm_json_tree')
    def get_llm_json_tree():
        return utils.llm_json_tree()

    @app.route('/api/add_node/<nombre>/<int:ascendente_id>', methods=['POST'])
    def add_node(nombre, ascendente_id):
        nodo_padre = NodoArbol.query.get(ascendente_id)
        if nodo_padre is None:
            return Response('Ascendente no existe', status=400)

        nodo = NodoArbol(nombre=nombre)
        db.session.add(nodo)
        db.session.commit()

        relacion = RelacionesNodo(ascendente_id=ascendente_id, descendente_id=nodo.nodoID)
        db.session.add(relacion)
        db.session.commit()

        return jsonify(message='Nodo agregado', status=200, nodoID=nodo.nodoID)

    @app.route('/api/delete_node/<int:nodo_id>', methods=['GET', 'DELETE'])
    def delete_node(nodo_id):
        nodo = NodoArbol.query.get(nodo_id)
        if nodo is None:
            return Response('Nodo no existe', status=400)

        db.session.delete(nodo)
        db.session.commit()

        return jsonify({'message' : 'Nodo eliminado', 'status' : 200})

    def delete_relaciones_descendentes(nodo_id):
        relaciones = RelacionesNodo.query.filter_by(descendente_id=nodo_id).all()
        for relacion in relaciones:
            db.session.delete(relacion)

    @app.route('/api/move_node/<int:nodo_id>/<int:ascendente_id>', methods=['GET', 'PUT'])
    def move_node(nodo_id, ascendente_id):

        nodo = NodoArbol.query.get(nodo_id)
        if nodo is None:
            return Response('Nodo no existe', status=400)

        nodo_padre = NodoArbol.query.get(ascendente_id)
        if nodo_padre is None:
            return Response('Ascendente no existe', status=400)

        if nodo_recursive(nodo_id, ascendente_id):
            return Response('No se puede mover el nodo, nodo recursivo', status=400)

        delete_relaciones_descendentes(nodo_id)
        relacion = RelacionesNodo(ascendente_id=ascendente_id, descendente_id=nodo_id)

        db.session.add(relacion)
        db.session.commit()

        return jsonify({'message': 'Nodo movido', 'status': 200})

    def nodo_recursive(nodo_id, ascendente_id):
        if nodo_id == ascendente_id:
            return True
        relaciones = RelacionesNodo.query.filter_by(ascendente_id=nodo_id).all()
        for relacion in relaciones:

            if nodo_recursive(relacion.descendente_id, ascendente_id):
                return True
        return False

    @app.route('/api/update_node/<int:nodo_id>/<nombre>', methods=['GET', 'PUT'])
    def update_node(nodo_id, nombre):
        nodo = NodoArbol.query.get(nodo_id)
        if nodo is None:
            return Response('Nodo no existe', status=400)

        nodo.nombre = nombre
        db.session.commit()

        return jsonify({'message': 'Nodo actualizado', 'status': 200})

    @app.route('/svg')
    def svg():
        return ("""
                        <svg height="100px" width="100px" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 512 512" xml:space="preserve" fill="#000000"><g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g><g id="SVGRepo_iconCarrier"> <path style="fill:#E2E5E7;" d="M128,0c-17.6,0-32,14.4-32,32v448c0,17.6,14.4,32,32,32h320c17.6,0,32-14.4,32-32V128L352,0H128z"></path> <path style="fill:#B0B7BD;" d="M384,128h96L352,0v96C352,113.6,366.4,128,384,128z"></path> <polygon style="fill:#CAD1D8;" points="480,224 384,128 480,128 "></polygon> <path style="fill:#F15642;" d="M416,416c0,8.8-7.2,16-16,16H48c-8.8,0-16-7.2-16-16V256c0-8.8,7.2-16,16-16h352c8.8,0,16,7.2,16,16 V416z"></path> <g> <path style="fill:#FFFFFF;" d="M101.744,303.152c0-4.224,3.328-8.832,8.688-8.832h29.552c16.64,0,31.616,11.136,31.616,32.48 c0,20.224-14.976,31.488-31.616,31.488h-21.36v16.896c0,5.632-3.584,8.816-8.192,8.816c-4.224,0-8.688-3.184-8.688-8.816V303.152z M118.624,310.432v31.872h21.36c8.576,0,15.36-7.568,15.36-15.504c0-8.944-6.784-16.368-15.36-16.368H118.624z"></path> <path style="fill:#FFFFFF;" d="M196.656,384c-4.224,0-8.832-2.304-8.832-7.92v-72.672c0-4.592,4.608-7.936,8.832-7.936h29.296 c58.464,0,57.184,88.528,1.152,88.528H196.656z M204.72,311.088V368.4h21.232c34.544,0,36.08-57.312,0-57.312H204.72z"></path> <path style="fill:#FFFFFF;" d="M303.872,312.112v20.336h32.624c4.608,0,9.216,4.608,9.216,9.072c0,4.224-4.608,7.68-9.216,7.68 h-32.624v26.864c0,4.48-3.184,7.92-7.664,7.92c-5.632,0-9.072-3.44-9.072-7.92v-72.672c0-4.592,3.456-7.936,9.072-7.936h44.912 c5.632,0,8.96,3.344,8.96,7.936c0,4.096-3.328,8.704-8.96,8.704h-37.248V312.112z"></path> </g> <path style="fill:#CAD1D8;" d="M400,432H96v16h304c8.8,0,16-7.2,16-16v-16C416,424.8,408.8,432,400,432z"></path> </g></svg>
                """)
        return 'SVG'


    #para probar
    @app.route('/api/prueba_funcion')
    def prueba_funcion():
        nodos_id = [1,10,7,32,8,9,26]
        nodo_conocimiento_completo = NodoArbol.query.filter(NodoArbol.nodoID.in_(nodos_id)).all()
        root_node_id = 1
        root_node = NodoArbol.query.filter_by(nodoID=root_node_id).first()

        nodos_id = [nodo.nodoID for nodo in nodo_conocimiento_completo]
        relaciones = RelacionesNodo.query.filter(RelacionesNodo.descendente_id.in_(nodos_id)).all()

        json = {}
        json_tree = utils.get_json_tree_from_unordered_nodes(root_node, nodo_conocimiento_completo, relaciones, json)

        return jsonify(json_tree)

