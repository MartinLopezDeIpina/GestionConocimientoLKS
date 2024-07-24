import json
from dataclasses import dataclass

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, PrimaryKeyConstraint, event
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.orm.attributes import get_history

import utils
from database import db


# dataclass hace que se pueda serializar automáticamente a JSON
@dataclass
class NodoArbol(db.Model):
    nodoID = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250), nullable=False)
    embedding = mapped_column(Vector(1536))


@event.listens_for(NodoArbol, 'after_update')
def update_node_embedding_after_update(mapper, connection, target):
    # Check if 'nombre' attribute was modified
    history = get_history(target, 'nombre')
    if history.has_changes():
        update_node_embeddings(target, connection)


def update_node_embeddings(nodo: NodoArbol, connection):
    nodos_ascendentes = utils.get_nodos_de_los_que_depende_nodo(nodo)
    nodos_ascendentes_nombre = list(map(lambda x: x.nombre, nodos_ascendentes))
    nodos_ascendentes_nombre.reverse()
    nodos_ascendentes_nombre.append(nodo.nombre)

    path_string = ' -> '.join(nodos_ascendentes_nombre)
    embedding = utils.get_embedding(path_string)

    connection.execute(
        NodoArbol.__table__.update().where(NodoArbol.nodoID == nodo.nodoID).values(embedding=embedding)
    )


class RelacionesNodo(db.Model):
    ascendente_id = db.Column(db.Integer, ForeignKey('nodo_arbol.nodoID', ondelete='CASCADE'))
    descendente_id = db.Column(db.Integer, ForeignKey('nodo_arbol.nodoID', ondelete='CASCADE'))

    nodo_ascendiente_id = relationship('NodoArbol', foreign_keys=[ascendente_id])
    nodo_descendiente_id = relationship('NodoArbol', foreign_keys=[descendente_id])

    __table_args__ = (PrimaryKeyConstraint('ascendente_id', 'descendente_id'), )


@event.listens_for(RelacionesNodo, 'after_insert')
def update_node_embedding_from_name_change(mapper, connection, target):
    history = get_history(target, 'descendente_id')
    target_nombre = db.session.query(NodoArbol).filter(NodoArbol.nodoID == target.descendente_id).first().nombre
    if history.has_changes() and target_nombre != ' ':
        nodos_a_actualizar_id = [target.descendente_id]

        nodos_hijos = utils.get_nodos_descendientes_id(target.descendente_id)
        nodos_a_actualizar_id.extend(nodos_hijos)

        nodos_a_actualizar = db.session.query(NodoArbol).filter(NodoArbol.nodoID.in_(nodos_a_actualizar_id)).all()
        for nodo in nodos_a_actualizar:
            update_node_embeddings(nodo, connection)


class Usuario(db.Model):
    email = db.Column(db.String(250), primary_key=True)
    nombre = db.Column(db.String(250), nullable=False)


class ConocimientoUsuario(db.Model):
    usuario_email = db.Column(db.String(250), ForeignKey('usuario.email'), primary_key=True)
    nodoID = db.Column(db.Integer, ForeignKey('nodo_arbol.nodoID', ondelete='CASCADE'), primary_key=True)
    nivel_IA = db.Column(db.Integer, nullable=True)
    nivel_validado = db.Column(db.Integer, nullable=True)

    usuario = relationship('Usuario', foreign_keys=[usuario_email])
    nodo = relationship('NodoArbol', foreign_keys=[nodoID])


