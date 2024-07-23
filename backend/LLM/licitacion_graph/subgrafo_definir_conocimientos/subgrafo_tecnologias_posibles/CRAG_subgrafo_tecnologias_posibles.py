from typing import TypedDict

from langgraph.constants import START
from langgraph.graph import StateGraph

import utils
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_tecnologias_posibles.Grader import \
    invoke_grader_get_tecnologias_validas, TecnologiaPuntuadaAlchemy
from LLM.llm_utils import LLM_utils
from models import NodoArbol


class State(TypedDict):
    herramienta_necesaria: str
    tecnologias_posibles: list[NodoArbol]
    tecnologias_puntuadas: list[TecnologiaPuntuadaAlchemy]
    reescrita: bool


def invoke_tecnologias_empresa_rag(state: State):
    herramienta_necesaria = state["herramienta_necesaria"]

    tecnologias_posibles = utils.nodo_arbol_semantic_search(herramienta_necesaria)

    return {"tecnologias_posibles": tecnologias_posibles}


def invoke_grader(state: State):
    herramienta = state["herramienta_necesaria"]
    propuestas = state["tecnologias_posibles"]

    propuestas_puntuadas = invoke_grader_get_tecnologias_validas(herramienta, propuestas)

    return {"tecnologias_aprobadas": propuestas_puntuadas}


def condicional_lista_vacia(state: State):
    propuestas_validas = filter(lambda x: x.puntuacion, state["tecnologias_puntuadas"])

    if propuestas_validas:
        return "mandar_tecnologias"
    else:
        return "condicional_reescribir"


def condicional_reescribir(state: State):
    reescrita = state["reescrita"]

    if reescrita:
        return "proponer_tecnologia_nueva"
    else:
        return "reescribir_herramienta_necesaria"


def invoke_re_writer(state: State):
    print("Invocando reescribir herramienta necesaria")


def invoke_proponer_tecnologia_nueva(state: State):
    print("Invocando proponer tecnologia nueva")


async def invoke_tecnologias_posibles_graph(herramienta_necesaria: str):
    workflow = StateGraph(State)

    workflow.add_node("tecnologias_empresa_rag", invoke_tecnologias_empresa_rag)
    workflow.add_node("grader", invoke_grader)

    workflow.add_edge(START, "tecnologias_empresa_rag")
    workflow.add_edge("tecnologias_empresa_rag", "grader")
    workflow.add_conditional_edges("condicional_lista_vacia", condicional_lista_vacia)
    workflow.add_edge("grader", "condicional_lista_vacia")
    workflow.add_conditional_edges("condicional_reescribir", condicional_reescribir)

    initial_state = State(
        herramienta_necesaria=herramienta_necesaria,
        tecnologias_posibles=[],
        tecnologias_puntuadas=[],
        reescrita=False,
    )

    graph = workflow.compile()

    async for output in graph.astream(initial_state, stream_mode="values"):
        print(output)
