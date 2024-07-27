from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.clases_para_lats import \
    PropuestaProyecto
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.subrafo_juntar_herramientas_de_etapa import \
    HerramientaJuntoTecnologiasPropuestas
from LLM.licitacion_graph.subgrafo_definir_requisitos_tecnicos.StageResult import StageResult
from models import NodoArbol


class DatosLicitacion:
    def __init__(self, licitacion: str, requisitos_adicionales: list[str], categoria_proyecto: str = "",
                 etapas_proyecto=None, requisitos_etapas: list[StageResult] = None):
        self.licitacion = licitacion
        self.requisitos_adicionales = requisitos_adicionales
        self.categoria_proyecto = categoria_proyecto
        self.etapas_proyecto = etapas_proyecto
        self.requisitos_etapas = requisitos_etapas

    def __str__(self):
        result = ""
        result += f"Licitacion: {self.licitacion}\n"
        result += f"Categoria: {self.categoria_proyecto}\n"
        result += f"Requisitos adicionales: {self.requisitos_adicionales}\n"
        result += f"Etapas proyecto: {self.get_requisitos_etapas_str()}\n"

    def get_requisitos_etapas_str(self) -> str:
        result = ""
        for etapa in self.requisitos_etapas:
            result += f"{etapa.get_final_etapa_str()}\n"

        return result

    def set_tecnologias_etapas(self, tecnologias_etapas: PropuestaProyecto):
        etapas = []
        for index_etapa, etapa in enumerate(tecnologias_etapas.etapas_proyecto):
            herramientas = []
            herramienta_junto_nodo = []
            for herramienta_junto_nodo_id in etapa.herramientas_junto_nodo_id_escogido:
                herramientas.append(herramienta_junto_nodo_id.herramienta)

                nodo = NodoArbol.query.get(herramienta_junto_nodo_id.nodo_id_escogido)
                if nodo:
                    herramienta_junto_nodo.append(HerramientaJuntoTecnologiasPropuestas(
                        herramienta=herramienta_junto_nodo_id.herramienta,
                        tecnologias=[nodo]
                    ))

            stage_result = StageResult(
                index_etapa=index_etapa,
                etapa=etapa.etapa,
                herramientas=herramientas,
                tecnologias_junto_herramientas=herramienta_junto_nodo
            )
            etapas.append(stage_result)
        self.requisitos_etapas = etapas


