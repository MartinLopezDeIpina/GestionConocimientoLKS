from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.subrafo_juntar_herramientas_de_etapa import \
    HerramientaJuntoTecnologiasPropuestas


class StageResult:
    etapa: str
    index_etapa: int
    herramientas: list[str]
    tecnologias_junto_herramientas: list[HerramientaJuntoTecnologiasPropuestas]

    def __init__(self, etapa: str, index_etapa: int, herramientas: list[str], tecnologias_junto_herramientas: list[HerramientaJuntoTecnologiasPropuestas] = None):
        self.etapa = etapa
        self.index_etapa = index_etapa
        self.herramientas = herramientas
        self.tecnologias_junto_herramientas = tecnologias_junto_herramientas

    def __str__(self):
        return f"\n{self.etapa}: \n{self.herramientas}"

    def get_final_etapa_str(self):
        result = f"\n{self.etapa}: \n"
        for tecnologias_h in self.tecnologias_junto_herramientas:
            result += f"\n{tecnologias_h["herramienta"]}:\n"
            for tecnologia in tecnologias_h["tecnologias"]:
                if tecnologia:
                    # No usar el serializador de NodoArbol porque no queremos pasar el embedding
                    nodo_dict = {"nodoID": tecnologia.nodoID, "nombre": tecnologia.nombre}
                    result += f"\t-{nodo_dict}\n"
        return result
