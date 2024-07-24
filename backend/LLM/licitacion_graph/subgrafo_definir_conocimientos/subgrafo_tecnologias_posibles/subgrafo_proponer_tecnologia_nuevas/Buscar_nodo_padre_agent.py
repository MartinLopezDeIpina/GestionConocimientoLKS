from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

from LLM.llm_utils import LLM_utils
from models import NodoArbol


class NodoID(BaseModel):
    """El id del nodo padre al que añadir la tecnología"""
    id: int = Field(description="id del nodo padre")


llm = LLM_utils.get_model()
structured_llm_father_searcher = llm.with_structured_output(NodoID)

system = """
Eres un agente especializado en determinar cuál es el nodo padre adecuado al que añadir la tecnología propuesta.
Se te proporcionará la tecnología propuesta junto a un árbol de conocimientos que representa el conocimiento de una empresa.
El árbol está formado por jerarquías de conocimientos, por ejemplo, el nodo de 'React' es hijo entre otros del nodo 'Frameworks Frontend'.
Tu tarea es determinar cuál es el nodo padre más adecuado para añadir la tecnología propuesta.
"""

father_search_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Tecnología: \n\n {tecnologia} \n\nArbol de conocimiento: {arbol}"),
    ]
)

father_searcher_agent = father_search_prompt | structured_llm_father_searcher


def invoke_buscar_nodo_padre_agent(tecnologia: str):
    arbol = NodoArbol.query.all()
    # No usar el serializador de NodoArbol porque no queremos pasar el embedding
    arbol_json = [{"nodoID": nodo.nodoID, "nombre": nodo.nombre} for nodo in arbol]

    nodo_padre_pydantic = father_searcher_agent.invoke({"tecnologia": tecnologia, "arbol": arbol_json})
    nodo_padre_id = nodo_padre_pydantic.id

    return nodo_padre_id
