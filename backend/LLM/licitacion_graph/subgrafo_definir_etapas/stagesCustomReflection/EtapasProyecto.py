from langchain_core.pydantic_v1 import BaseModel, Field


class EtapasProyecto(BaseModel):
    etapas: list[str] = Field(description="Lista de etapas técnicas del proyecto")
