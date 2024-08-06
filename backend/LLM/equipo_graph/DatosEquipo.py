from typing import Dict, List

from models import NodoArbol


class DatosEquipo:
    cantidad_trabajadores: int
    composicion_puestos_de_trabajo: Dict[str, int]
    tecnologias_por_puesto: Dict[str, List[int]]
    composicion_trabajadores: Dict[str, List[str]]

    def __init__(self, cantidad_trabajadores: int = 0, composicion_puestos_de_trabajo: dict = {}, tecnologias_por_puesto: dict={}, composicion_trabajadores: dict={}):
        self.cantidad_trabajadores = cantidad_trabajadores
        self.composicion_puestos_de_trabajo = composicion_puestos_de_trabajo
        self.tecnologias_por_puesto = tecnologias_por_puesto
        self.composicion_trabajadores = composicion_trabajadores

    def get_resultado_final_str(self):
        result = "-- Elección de trabajadores --\n\n"

        for puesto, trabajadores in self.composicion_trabajadores.items():
            result += f"-Puesto {puesto}:\n"

            conocimientos_ids_puesto = self.tecnologias_por_puesto[puesto]
            conocimientos_nodos_puesto = NodoArbol.query.filter(NodoArbol.nodoID.in_(conocimientos_ids_puesto)).all()
            formatted_nodos = [f"{nodo.nodoID}: {nodo.nombre}" for nodo in conocimientos_nodos_puesto]
            nodos_string = ", ".join(formatted_nodos)
            result += f"\tConocimientos necesarios: {nodos_string}\n"

            for trabajador in trabajadores:
                result += f"\tTrabajador: {trabajador}\n"

            result += "\n"

        return result

