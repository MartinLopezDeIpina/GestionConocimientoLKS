from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.subrafo_juntar_herramientas_de_etapa import \
    HerramientaJuntoTecnologiasPropuestas


class StageResult:
    def __init__(self, etapa: str, index_etapa: int, herramientas: list[str], tecnologias_junto_herramientas: list[HerramientaJuntoTecnologiasPropuestas] = None):
        self.etapa = etapa
        self.index_etapa = index_etapa
        self.herramientas = herramientas
        self.tecnologias_junto_herramientas = tecnologias_junto_herramientas

    def __str__(self):
        return f"\n{self.etapa}: \n{self.herramientas}"
