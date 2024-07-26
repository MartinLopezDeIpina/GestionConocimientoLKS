from pydantic.v1 import BaseModel, Field


class HerramientaJuntoNodoID(BaseModel):
    """Herramienta necesaria para una etapa de proyecto software junto con el nodo ID de la tecnología escogida"""
    herramienta: str = Field(description="Herramienta necesaria")
    nombre_nodo_escogido: str = Field(description="Nombre del nodo de la tecnología escogida")
    nodo_id_escogido: int = Field(description="Nodo ID de la tecnología escogida")


class PropuestaEtapa(BaseModel):
    """Propuesta de etapa de proyecto software, con sus herramientas necesarias y las tecnologías escogidas"""
    etapa: str = Field(description="Etapa del proyecto")
    herramientas_junto_nodo_id_escogido: list[HerramientaJuntoNodoID]


class PropuestaProyecto(BaseModel):
    """Propuesta de proyecto software, con sus etapas y tecnologías necesarias"""
    etapas_proyecto: list[PropuestaEtapa] = Field(description="Etapas del proyecto")
