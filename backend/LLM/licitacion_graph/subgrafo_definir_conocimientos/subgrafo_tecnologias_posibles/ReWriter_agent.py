from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

from LLM.llm_utils import LLM_utils
from models import NodoArbol


class ReWritedHerramientaNecesaria(BaseModel):
    """Herramienta necesaria para un proyecto software"""
    herramienta: str = Field(description="Herramienta necesaria")


llm = LLM_utils.get_model()
structured_llm_grader = llm.with_structured_output(ReWritedHerramientaNecesaria)

system = """
Eres un agente especializado en reescribir una herramienta necesaria para un proyecto software.
La herramienta neceesaria se buscará posteriormente en un sistema RAG que devolverá el conjunto de tecnologías válidas para representar la herramienta.
Se te van a proporcionar la herramienta necesaria y un conjunto de propuestas de tecnologías que no fueron válidas para representar la herramienta.
Reescribe la herramienta de forma que el sistema RAG encuentre las tecnologías válidas.
"""

grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Herramienta necesaria: \n\n {herramienta} \n\n Propuestas de tecnologías: {propuestas}"),
    ]
)

rewriter_agent = grade_prompt | structured_llm_grader


def invoke_rewriter_get_herramienta_reescrita(herramienta: str, propuestas: list[NodoArbol]):
    # No añadir el embedding para no pasárselo al LLM
    propuesta_json = [{"nodoID": propuesta.nodoID, "nombre": propuesta.nombre} for propuesta in propuestas]
    herramienta = rewriter_agent.invoke({"herramienta": herramienta, "propuestas": propuesta_json})

    herramienta_str = herramienta.herramienta

    return herramienta_str
