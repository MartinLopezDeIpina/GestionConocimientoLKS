from langchain_core.pydantic_v1 import BaseModel, Field

from LLM.agents.stagesCustomReflection.EtapasProyecto import EtapasProyecto


class EtapasProyectoJustificadas(BaseModel):
    explicacion: str = Field(description="Explicación de las modificaciones realizadas en las etapas del proyecto")
    referencias: list[str] = Field(description="Referencias que respaldan las modificaciones realizadas en las etapas del proyecto")
    etapas: EtapasProyecto = Field(description="Etapas técnicas del proyecto")
