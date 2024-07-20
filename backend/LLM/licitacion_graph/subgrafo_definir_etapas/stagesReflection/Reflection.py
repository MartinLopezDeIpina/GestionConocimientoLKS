from langchain_core.pydantic_v1 import BaseModel, Field


class Reflection(BaseModel):
    falta: str = Field(description="Crítica de lo que falta")
    sobra: str = Field(description="Crítica de los supérfluo")
