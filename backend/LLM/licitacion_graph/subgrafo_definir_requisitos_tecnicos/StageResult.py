from pydantic.v1 import BaseModel

from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.subrafo_juntar_herramientas_de_etapa import \
    HerramientaJuntoTecnologiasPropuestas
from models import NodoArbol


class StageResult(BaseModel):
    etapa: str
    index_etapa: int
    herramientas: list[str]
    tecnologias_junto_herramientas: list[HerramientaJuntoTecnologiasPropuestas]

    # En pydantic hay que poner esto para que pueda serializar clases que no sean de pydantic. En este caso, NodoArbol que está dentro de HerramientaJuntoTecnologiasPropuestas
    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        return f"\n{self.etapa}: \n{self.herramientas}"

    def get_final_etapa_str(self):
        result = f"\n{self.etapa}: \n"
        for tecnologias_h in self.tecnologias_junto_herramientas:
            result += f"\n{tecnologias_h["herramienta"]}:\n"
            for tecnologia in tecnologias_h["tecnologias_ids"]:
                if tecnologia:
                    nodo = NodoArbol.query.get(tecnologia)
                    nodo_dict = {"nodoID": nodo.nodoID, "nombre": nodo.nombre}
                    result += f"\t-{nodo_dict}\n"
        return result
