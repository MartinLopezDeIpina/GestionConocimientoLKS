from langchain_core.pydantic_v1 import BaseModel, Field

from LLM.agents.stagesCustomReflection.Reflection import Reflection


class AnswerQuestion(BaseModel):
    reflexion: Reflection = Field(description="La reflexión de la respuesta")
    search_queries: list[str] = Field(
        description="1-3 consultas de búsqueda para investigar mejoras con el fin de abordar la crítica de su respuesta actual."
    )
