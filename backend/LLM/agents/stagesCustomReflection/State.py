from typing import TypedDict, Union

from LLM.agents.stagesCustomReflection.EtapasProyecto import EtapasProyecto
from LLM.agents.stagesCustomReflection.AnswerQuestion import AnswerQuestion
from LLM.agents.stagesCustomReflection.EtapasProyectoJustificadas import EtapasProyectoJustificadas


class State(TypedDict):
    licitacion: str
    requisitos_adicionales: list[str]
    categoria_proyecto: str
    propuesta_etapas: Union[EtapasProyecto, EtapasProyectoJustificadas]
    critica_actual: AnswerQuestion
    resultados_busqueda: str
    num_iteraciones: int
    validation_error: str
