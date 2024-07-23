from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

from LLM.llm_utils import LLM_utils
from models import NodoArbol


class NodoArbolPydantic(BaseModel):
    """Nodo del árbol de conocimientos"""
    nodoID: int = Field(description="Identificador del nodo")
    nombre: str = Field(description="Nombre del conociemiento")
    vector: list[float] = Field(description="Vector de embeddings del conocimiento")

    def map_to_alchemy_model(self):
        return NodoArbol(nodoID=self.nodoID, nombre=self.nombre, vector=self.vector)



class TecnologiaPuntuadaPydantic(BaseModel):
    """Tecnología propuesta y su puntuación binaria"""
    tecnologia: NodoArbolPydantic = Field(description="Tecnología propuesta")
    puntuacion: bool = Field(description="Puntuación binaria de la tecnología")

    def map_to_alchemy_model(self):
        return TecnologiaPuntuadaAlchemy(tecnologia=self.tecnologia.map_to_alchemy_model(), puntuacion=self.puntuacion)


class GradeDocumentsPydantic(BaseModel):
    """Puntuación binaria para verificar la validez de las tecnologías recuperados."""
    puntuacion_binaria: list[TecnologiaPuntuadaPydantic] = Field(description="Las tecnologías son una propuesta válida True o False")

    def map_to_alchemy_model(self):
        return GradeDocumentsAlchemy(puntuacion_binaria=[tecnologia.map_to_alchemy_model() for tecnologia in self.puntuacion_binaria])


class TecnologiaPuntuadaAlchemy:
    """Tecnología propuesta y su puntuación binaria"""
    tecnologia: NodoArbol
    puntuacion: bool


class GradeDocumentsAlchemy:
    """Puntuación binaria para verificar la validez de las tecnologías recuperados."""
    puntuacion_binaria: list[TecnologiaPuntuadaAlchemy]


llm = LLM_utils.get_model()
structured_llm_grader = llm.with_structured_output(GradeDocumentsPydantic)

system = """Eres un agente especializado en determinar la validez de tecnologías de desarrollo software para representar una herramienta necesaria.
Se te va a presentar un tipo de herramienta necesaria, junto con varias propuestas de tecnologías.
Debes evaluar por cada una de las propuestas si es válida o no para representar la herramienta necesaria.

Por ejemplo, para la herramienta 'Framework Frontend', 'React' o 'Angular' serían propuestas válidas, mientras que 'HTML' o 'CSS' no lo serían, ya que estas no son frameworks sino lenguajes.
"""

grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Herramienta necesaria: \n\n {herramienta} \n\n Propuestas de tecnologías: {propuestas}"),
    ]
)

retrieval_grader = grade_prompt | structured_llm_grader


def invoke_grader_get_tecnologias_validas(herramienta: str, propuestas: list[NodoArbol]):
    #Usar los modelos de pydantic para validar la salida del LLM, y los modelos de Alchemy (NodoArbol) para lo demás
    propuestas_puntuadas = retrieval_grader.invoke({"herramienta": herramienta, "propuestas": propuestas})
    propuestas_puntuadas_alchemy = propuestas_puntuadas.map_to_alchemy_model()

    return propuestas_puntuadas_alchemy
