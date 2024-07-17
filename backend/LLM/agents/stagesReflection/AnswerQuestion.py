from langchain_core.pydantic_v1 import BaseModel, Field
from LLM.agents.stagesReflection.Reflection import Reflection


class AnswerQuestion(BaseModel):
    """Answer the question. Provide an answer, reflection, and then follow up with search queries to improve the answer."""

    etapas: list[str] = Field(description="Lista de etapas del proyecto, cada una con una descripción general de la etapa.")
    reflexion: Reflection = Field(description="La reflexión de la respuesta")
    search_queries: list[str] = Field(
        description="1-3 consultas de búsqueda para investigar mejoras con el fin de abordar la crítica de su respuesta actual."
    )
