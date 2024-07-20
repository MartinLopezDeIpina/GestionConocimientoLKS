from LLM.licitacion_graph.subgrafo_definir_requisitos_tecnicos.StageResult import StageResult


class DatosLicitacion:
    def __init__(self, licitacion: str, requisitos_adicionales: list[str], categoria_proyecto: str = "",
                 etapas_proyecto=None, requisitos_etapas: list[StageResult] = None):
        self.licitacion = licitacion
        self.requisitos_adicionales = requisitos_adicionales
        self.categoria_proyecto = categoria_proyecto
        self.etapas_proyecto = etapas_proyecto
        self.requisitos_etapas = requisitos_etapas
