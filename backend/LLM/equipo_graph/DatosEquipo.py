from typing import Dict, List


class DatosEquipo:
    cantidad_trabajadores: int
    composicion_puestos_de_trabajo: Dict[str, int]
    tecnologias_por_puesto: Dict[str, List[int]]
    composicion_trabajadores: dict

    def __init__(self, cantidad_trabajadores: int = 0, composicion_puestos_de_trabajo: dict = {}, tecnologias_por_puesto: dict={}, composicion_trabajadores: dict={}):
        self.cantidad_trabajadores = cantidad_trabajadores
        self.composicion_puestos_de_trabajo = composicion_puestos_de_trabajo
        self.tecnologias_por_puesto = tecnologias_por_puesto
        self.composicion_trabajadores = composicion_trabajadores
