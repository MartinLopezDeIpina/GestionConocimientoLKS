import operator
from typing import TypedDict, Annotated
from langgraph.constants import START, END, Send
from langgraph.graph import StateGraph

from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.subgrafo_tecnologias_posibles_herramienta.CRAG_subgrafo_tecnologias_posibles import \
    invoke_tecnologias_posibles_graph
from models import NodoArbol


class StateHerramienta(TypedDict):
    herramienta_necesaria: str
    result: list[NodoArbol]


class State(TypedDict):
    herramientas_necesarias: list[str]
    resultados_herramientas: Annotated[list[list[NodoArbol]], operator.add]


def invoke_herramientas(state: State):
    herramientas = state["herramientas_necesarias"]

    return [Send("ejecutar_herramienta",
                 {
                     "herramienta_necesaria": herramienta,
                 }) for herramienta in herramientas]


def ejecutar_herramienta(state: StateHerramienta):
    herramienta_necesaria = state["herramienta_necesaria"]

    result = invoke_tecnologias_posibles_graph(herramienta_necesaria)

    return {"resultados_herramientas": [result]}


def invoke_subgrafo_juntar_herramientas_de_etapa(herramientas_necesarias: list[str]):
    workflow = StateGraph(State)

    workflow.add_node("ejecutar_herramienta", ejecutar_herramienta)

    workflow.add_conditional_edges(START, invoke_herramientas, ["ejecutar_herramienta"])
    workflow.add_edge("ejecutar_herramienta", END)

    initial_state = State(
        herramientas_necesarias=herramientas_necesarias,
        resultados_herramientas=[]
    )

    graph = workflow.compile()
    result = graph.invoke(initial_state)
    return result["resultados_herramientas"]



