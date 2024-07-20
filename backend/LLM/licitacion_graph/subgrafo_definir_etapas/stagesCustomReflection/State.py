from typing import TypedDict, Union

from LLM.licitacion_graph.subgrafo_definir_etapas.stagesCustomReflection.EtapasProyecto import EtapasProyecto
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesCustomReflection.AnswerQuestion import AnswerQuestion
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesCustomReflection.EtapasProyectoJustificadas import EtapasProyectoJustificadas


class State(TypedDict):
    licitacion: str
    requisitos_adicionales: list[str]
    categoria_proyecto: str
    propuesta_etapas: Union[EtapasProyecto, EtapasProyectoJustificadas]
    critica_actual: AnswerQuestion
    resultados_busqueda: str
    num_iteraciones: int
    validation_error: str
