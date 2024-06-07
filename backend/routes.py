import csv
import os

from flask import Response, jsonify
from treelib import Tree

from database import db
from models import NodoArbol, RelacionesNodo

def init_routes(app):
    # Sólo para probar
    @app.route('/api/add_csv')
    def store_tree_from_csv():
        file_path = os.path.join(app.static_folder, 'conocimientos.csv')

        # Keep track of the last node at each depth level
        last_node_at_depth = {}

        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                # Iterate over each cell in the row
                for i in range(len(row)):
                    node = row[i]

                    # Skip empty cells
                    if not node:
                        continue

                    parent = last_node_at_depth.get(i - 1)

                    nodo = NodoArbol(nombre=node)
                    #nodo = NodoArbol.query.order_by(-NodoArbol.nombre).first()
                    db.session.add(nodo)
                    db.session.commit()

                    # If the node is not the root node, create a relationship with its parent
                    if parent:
                        parent_nodo = NodoArbol.query.filter_by(nombre=parent).first()
                        relacion = RelacionesNodo(ascendente_id=parent_nodo.nodoID, descendente_id=nodo.nodoID)
                        db.session.add(relacion)
                        db.session.commit()

                    # Update the last node at the current depth level
                    last_node_at_depth[i] = node

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
        relaciones = RelacionesNodo.query.all()
        nodo_dict = {nodo.nodoID: nodo for nodo in nodos}

        json = {}
        add_node_to_json(json, nodos[0], relaciones, nodo_dict)

        return [json]

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

        delete_relaciones_ascendentes(nodo_id)
        delete_relaciones_descendentes(nodo_id)

        db.session.delete(nodo)
        db.session.commit()

        return jsonify({'message' : 'Nodo eliminado', 'status' : 200})

    def delete_relaciones_ascendentes(nodo_id):
        relaciones = RelacionesNodo.query.filter_by(ascendente_id=nodo_id).all()
        for relacion in relaciones:
            delete_node(relacion.descendente_id)
            db.session.delete(relacion)

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

        return Response('Nodo movido', status=200)

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

    @app.route('/api/seed')
    def seed():
        seed_data = [
            {
                "id": "123",
                "title": "company",
                "subtitle": "zzz",
                "isdirectory": True,
                "expanded": False,
                "children": [
                    {"id": "456", "title": "human resource", "subtitle": "zzz"},
                    {
                        "id": "789",
                        "title": "bussiness",
                        "subtitle": "zzz",
                        "expanded": False,
                        "children": [
                            {
                                "id": "234",
                                "title": "store a",
                                "subtitle": "zzz"
                            },
                            {"id": "567", "title": "store b", "subtitle": "zzz"}
                        ]
                    }
                ]
            }
        ]

        return seed_data


