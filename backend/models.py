from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from database import db


class NodoArbol(db.Model):
    nodoID = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250), nullable=False)


class RelacionesNodo(db.Model):
    ascendente_id = db.Column(db.Integer, ForeignKey('nodo_arbol.nodoID'))
    descendente_id = db.Column(db.Integer, ForeignKey('nodo_arbol.nodoID'))

    nodo_ascendiente_id = relationship('NodoArbol', foreign_keys=[ascendente_id])
    nodo_descendiente_id = relationship('NodoArbol', foreign_keys=[descendente_id])

    __table_args__ = (PrimaryKeyConstraint('ascendente_id', 'descendente_id'), )
