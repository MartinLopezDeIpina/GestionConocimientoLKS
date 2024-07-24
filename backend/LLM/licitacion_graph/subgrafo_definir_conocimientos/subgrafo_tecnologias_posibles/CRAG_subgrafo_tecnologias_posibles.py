from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph

import utils
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_tecnologias_posibles.Grader_agent import \
    invoke_grader_get_tecnologias_validas
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_tecnologias_posibles.ReWriter_agent import \
    invoke_rewriter_get_herramienta_reescrita
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_tecnologias_posibles.subgrafo_proponer_tecnologia_nuevas.subgrafo_proponer_tecnologias_nuevas import \
    invoke_subgrafo_proponer_tecnologia_nueva
from models import NodoArbol


class State(TypedDict):
    herramienta_necesaria: str
    tecnologias_posibles: list[NodoArbol]
    tecnologias_aprobadas: list[NodoArbol]
    reescrita: bool


def invoke_tecnologias_empresa_rag(state: State):
    herramienta_necesaria = state["herramienta_necesaria"]

    tecnologias_posibles = utils.nodo_arbol_semantic_search(herramienta_necesaria)

    return {"tecnologias_posibles": tecnologias_posibles}


def invoke_grader(state: State):
    herramienta = state["herramienta_necesaria"]
    propuestas = state["tecnologias_posibles"]

    tecnologias_aprobadas = invoke_grader_get_tecnologias_validas(herramienta, propuestas)

    return {"tecnologias_aprobadas": tecnologias_aprobadas}


def conditional_lista_vacia_rewriter(state: State):
    propuestas_validas = state["tecnologias_aprobadas"]
    reescrita = state["reescrita"]

    if propuestas_validas:
        return END
    elif reescrita:
        return "proponer_tecnologia_nueva"
    else:
        return "reescribir_herramienta_necesaria"


def invoke_proponer_tecnologia_nueva(state: State):
    herramienta_necesaria = state["herramienta_necesaria"]
    tecnologias_propuestas = state["tecnologias_posibles"]
    nodo_tecnologia_nueva = invoke_subgrafo_proponer_tecnologia_nueva(herramienta_necesaria, tecnologias_propuestas)

    if nodo_tecnologia_nueva:
        return {"tecnologias_aprobadas": [nodo_tecnologia_nueva]}


def invoke_re_writer(state: State):
    herramienta_necesaria = state["herramienta_necesaria"]
    tecnologias_propuestas = state["tecnologias_posibles"]

    herramienta_reescrita = invoke_rewriter_get_herramienta_reescrita(herramienta_necesaria, tecnologias_propuestas)

    return {"reescrita": True, "herramienta_necesaria": herramienta_reescrita}


def invoke_tecnologias_posibles_graph(herramienta_necesaria: str):
    workflow = StateGraph(State)

    workflow.add_node("tecnologias_empresa_rag", invoke_tecnologias_empresa_rag)
    workflow.add_node("grader", invoke_grader)
    workflow.add_node("reescribir_herramienta_necesaria", invoke_re_writer)
    workflow.add_node("proponer_tecnologia_nueva", invoke_proponer_tecnologia_nueva)

    workflow.add_edge(START, "tecnologias_empresa_rag")
    workflow.add_edge("tecnologias_empresa_rag", "grader")
    workflow.add_conditional_edges("grader", conditional_lista_vacia_rewriter)
    workflow.add_edge("reescribir_herramienta_necesaria", "tecnologias_empresa_rag")
    workflow.add_edge("proponer_tecnologia_nueva", END)

    initial_state = State(
        herramienta_necesaria=herramienta_necesaria,
        tecnologias_posibles=[],
        tecnologias_aprobadas=[],
        reescrita=False,
    )

    graph = workflow.compile()
    result = graph.invoke(initial_state)

    return result["tecnologias_aprobadas"]


