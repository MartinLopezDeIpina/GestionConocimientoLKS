from typing import TypedDict
from LLM.agents.stagesReflection.AnswerQuestion import AnswerQuestion


class State(TypedDict):
    licitacion: str
    requisitos_adicionales: list[str]
    categoria_proyecto: str
    critica_actual: AnswerQuestion
    resultados_busqueda: str
    num_iteraciones: int
