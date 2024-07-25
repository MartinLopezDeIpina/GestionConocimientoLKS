from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

from LLM.llm_utils import LLM_utils
from database import db
from models import NodoArbol


class NodoArbolPydantic(BaseModel):
    """Nodo del árbol de conocimientos"""
    nodoID: int = Field(description="Identificador del nodo")
    nombre: str = Field(description="Nombre del conociemiento")


class TecnologiaPuntuadaPydantic(BaseModel):
    """Tecnología propuesta y su puntuación binaria"""
    tecnologia: NodoArbolPydantic = Field(description="Tecnología propuesta")
    puntuacion: bool = Field(description="Puntuación binaria de la tecnología")


class GradeDocumentsPydantic(BaseModel):
    """Puntuación binaria para verificar la validez de las tecnologías recuperados."""
    puntuacion_binaria: list[TecnologiaPuntuadaPydantic] = Field(description="Las tecnologías son una propuesta válida True o False")

    def map_graded_documents_to_passed_node_list(self) -> list[NodoArbol]:
        nodos = []
        for documento in self.puntuacion_binaria:
            if documento.puntuacion:
                nodo = NodoArbol.query.filter(NodoArbol.nodoID == documento.tecnologia.nodoID).first()
                nodos.append(nodo)

        return nodos


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
    # No añadir el embedding para no pasárselo al LLM
    propuesta_json = [{"nodoID": propuesta.nodoID, "nombre": propuesta.nombre} for propuesta in propuestas]
    propuestas_puntuadas = retrieval_grader.invoke({"herramienta": herramienta, "propuestas": propuesta_json})

    nodos = propuestas_puntuadas.map_graded_documents_to_passed_node_list()

    return nodos
