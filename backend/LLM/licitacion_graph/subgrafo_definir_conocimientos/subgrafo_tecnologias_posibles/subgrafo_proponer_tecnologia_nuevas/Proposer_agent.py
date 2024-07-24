from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from pydantic.v1 import conlist

from LLM.llm_utils import LLM_utils
from database import db
from models import NodoArbol


class TecnologiaPropuesta(BaseModel):
    """Tecnología propuesta para representar la herramienta necesaria en el proyecto software"""
    nombre: str = Field(description="Nombre de la tecnología")


llm = LLM_utils.get_model()
structured_llm_grader = llm.with_structured_output(TecnologiaPropuesta)

system = """
Eres un agente especializado en proporcionar tecnologías válidas para una herramienta necesaria para un proyecto software.
Se te van a proporcionar la herramienta necesaria y un conjunto de propuestas de tecnologías que no fueron válidas para representar la herramienta.
Proporciona la tecnología que más apropiada consideres en el mercado actual para representar la herramienta.
Por ejemplo, si la herramienta necesaria es 'Framework Frontend', podrías proponer 'React' o 'Angular', ya que son los frameworks más utilizados en la actualidad.
"""

grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Herramienta necesaria: \n\n {herramienta} \n\n Propuestas de tecnologías no satisfactorias: {propuestas}"),
    ]
)

proposer_agent = grade_prompt | structured_llm_grader


def invoke_proposer_get_tecnologia_propuesta(herramienta: str, propuestas: list[NodoArbol]):
    # No añadir el embedding para no pasárselo al LLM
    propuesta_json = [{"nodoID": propuesta.nodoID, "nombre": propuesta.nombre} for propuesta in propuestas]
    tecnologia_propuesta = proposer_agent.invoke({"herramienta": herramienta, "propuestas": propuesta_json})
    tecnologia_propuesta_str = tecnologia_propuesta.nombre

    return tecnologia_propuesta_str
