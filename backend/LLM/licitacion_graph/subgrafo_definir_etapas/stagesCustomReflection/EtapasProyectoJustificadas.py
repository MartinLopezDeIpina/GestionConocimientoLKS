from langchain_core.pydantic_v1 import BaseModel, Field


class EtapasProyectoJustificadas(BaseModel):
    referencias: list[str] = Field(description="Referencias que respaldan las modificaciones realizadas en las etapas del proyecto. Cada referencia debe estar enumerada para poder ser citada: [1] ejemplodepagina.com/algo  [2] otroejemplo.com/otracosa")
    explicacion: str = Field(description="Explicación de las modificaciones realizadas en las etapas del proyecto")
    etapas: list[str] = Field(description="Lista de etapas técnicas del proyecto")
