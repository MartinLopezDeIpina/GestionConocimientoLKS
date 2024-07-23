from typing import TypedDict

from langgraph.constants import START
from langgraph.graph import StateGraph

import utils
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_tecnologias_posibles.Grader import \
    invoke_grader_get_tecnologias_validas, TecnologiaPuntuadaPydantic
from LLM.llm_utils import LLM_utils
from models import NodoArbol


class State(TypedDict):
    herramienta_necesaria: str
    tecnologias_posibles: list[NodoArbol]
    tecnologias_puntuadas: list[TecnologiaPuntuadaPydantic]
    reescrita: bool


def invoke_tecnologias_empresa_rag(state: State):
    herramienta_necesaria = state["herramienta_necesaria"]

    tecnologias_posibles = utils.nodo_arbol_semantic_search(herramienta_necesaria)

    return {"tecnologias_posibles": tecnologias_posibles}


def invoke_grader(state: State):
    herramienta = state["herramienta_necesaria"]
    propuestas = state["tecnologias_posibles"]

    propuestas_puntuadas = invoke_grader_get_tecnologias_validas(herramienta, propuestas)

    return {"tecnologias_puntuadas": propuestas_puntuadas}


def conditional_lista_vacia_rewriter(state: State):
    propuestas_validas = filter(lambda x: x.puntuacion, state["tecnologias_puntuadas"])
    reescrita = state["reescrita"]

    if propuestas_validas:
        return "mandar_tecnologias"
    elif reescrita:
        return "proponer_tecnologia_nueva"
    else:
        return "reescribir_herramienta_necesaria"


def invoke_re_writer(state: State):
    print("Invocando reescribir herramienta necesaria")
    return {"reescrita": True}


def invoke_proponer_tecnologia_nueva(state: State):
    print("Invocando proponer tecnologia nueva")
    return {"herramienta_necesaria": "algo"}


def invoke_tecnologias_posibles_graph(herramienta_necesaria: str):
    workflow = StateGraph(State)

    workflow.add_node("tecnologias_empresa_rag", invoke_tecnologias_empresa_rag)
    workflow.add_node("grader", invoke_grader)
    workflow.add_node("reescribir_herramienta_necesaria", invoke_re_writer)
    workflow.add_node("proponer_tecnologia_nueva", invoke_proponer_tecnologia_nueva)

    workflow.add_edge(START, "tecnologias_empresa_rag")
    workflow.add_edge("tecnologias_empresa_rag", "grader")
    workflow.add_conditional_edges("grader", conditional_lista_vacia_rewriter)

    initial_state = State(
        herramienta_necesaria=herramienta_necesaria,
        tecnologias_posibles=[],
        tecnologias_puntuadas=[],
        reescrita=False,
    )

    graph = workflow.compile()
    graph.invoke(initial_state)


