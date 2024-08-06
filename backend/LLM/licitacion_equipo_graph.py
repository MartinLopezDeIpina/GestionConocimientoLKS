from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from LLM.equipo_graph.DatosEquipo import DatosEquipo
from LLM.equipo_graph.equipo_graph import start_equipo_graph
from LLM.licitacion_graph.DatosLicitacion import DatosLicitacion
from LLM.licitacion_graph.LicitacionGraph import start_licitacion_graph


class State(TypedDict):
    licitacion: str
    requisitos_adicionales: list[str]
    datos_licitacion: DatosLicitacion
    datos_equipo: DatosEquipo


def node_invoke_licitacion_graph(state: State):
    licitacion = state["licitacion"]
    requisitos_adicionales = state["requisitos_adicionales"]

    datos_licitacion = start_licitacion_graph(licitacion, requisitos_adicionales)

    return {"datos_licitacion": datos_licitacion}


def node_invoke_equipo_graph(state: State):
    datos_licitacion = state["datos_licitacion"]

    datos_equipo = start_equipo_graph(datos_licitacion)

    return {"datos_equipo": datos_equipo}


def invoke_licitacion_equipo_graph(licitacion: str, requisitos_adicionales: list[str]):
    workflow = StateGraph(State)

    workflow.add_node("node_invoke_licitacion_graph", node_invoke_licitacion_graph)
    workflow.add_node("node_invoke_equipo_graph", node_invoke_equipo_graph)

    workflow.add_edge(START, "node_invoke_licitacion_graph")
    workflow.add_edge("node_invoke_licitacion_graph", "node_invoke_equipo_graph")
    workflow.add_edge("node_invoke_equipo_graph", END)

    initial_state = State(
        licitacion=licitacion,
        requisitos_adicionales=requisitos_adicionales,
        datos_licitacion=None,
        datos_equipo=None
    )

    graph = workflow.compile()

    result = graph.invoke(initial_state)

    return result



