from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from database import db


class NodoArbol(db.Model):
    nodoID = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250), nullable=False)


class RelacionesNodo(db.Model):
    ascendente_id = db.Column(db.Integer, ForeignKey('nodo_arbol.nodoID', ondelete='CASCADE'))
    descendente_id = db.Column(db.Integer, ForeignKey('nodo_arbol.nodoID', ondelete='CASCADE'))

    nodo_ascendiente_id = relationship('NodoArbol', foreign_keys=[ascendente_id])
    nodo_descendiente_id = relationship('NodoArbol', foreign_keys=[descendente_id])

    __table_args__ = (PrimaryKeyConstraint('ascendente_id', 'descendente_id'), )


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


