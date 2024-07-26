import operator
from typing import TypedDict, Annotated
from langgraph.constants import START, Send, END
from langgraph.graph import StateGraph
from LLM.licitacion_graph.DatosLicitacion import DatosLicitacion
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.agente_selector_tecnologias import \
    invoke_seleccionar_tecnologias, PropuestaProyecto
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.subrafo_juntar_herramientas_de_etapa import \
    invoke_subgrafo_juntar_herramientas_de_etapa
from LLM.licitacion_graph.subgrafo_definir_requisitos_tecnicos.StageResult import StageResult
from models import NodoArbol


class State(TypedDict):
    datos_licitacion: DatosLicitacion
    requisitos_etapas: Annotated[list[StageResult], operator.add]


class StateEtapa(TypedDict):
    requisitos_etapa: StageResult


def invoke_cada_etapa_tecnologias_posibles(state: State):
    datos_licitacion = state["datos_licitacion"]
    requisitos_etapas = datos_licitacion.requisitos_etapas

    return [Send("invoke_cada_herramienta_dentro_de_etapa_crag_subgraph",
                 {
                        "requisitos_etapa": requisitos_etapa,
                 }) for requisitos_etapa in requisitos_etapas]


def invoke_cada_herramienta_dentro_de_etapa_crag_subgraph(state: StateEtapa):
    requisitos_etapa = state["requisitos_etapa"]

    herramientas_necesarias = requisitos_etapa.herramientas

    herramientas_junto_tecnologias = invoke_subgrafo_juntar_herramientas_de_etapa(herramientas_necesarias)
    requisitos_etapa.tecnologias_junto_herramientas = herramientas_junto_tecnologias

    return {"requisitos_etapas": [requisitos_etapa]}


def juntar_etapas(state: State):
    datos_licitacion = state["datos_licitacion"]

    sorted_results = sorted(state["requisitos_etapas"], key=lambda x: x.index_etapa, reverse=True)

    datos_licitacion.requisitos_etapas = sorted_results
    return {"datos_licitacion": datos_licitacion}


def invoke_agente_selector_tecnologias(state: State):
    datos_licitacion = state["datos_licitacion"]

    propuesta_proyecto = invoke_seleccionar_tecnologias(datos_licitacion)

    datos_licitacion.set_tecnologias_etapas(propuesta_proyecto)

    return {"datos_licitacion": datos_licitacion}



def invoke_tecnologias_posibles_graph_lats(datos_licitacion: DatosLicitacion):
    workflow = StateGraph(State)

    workflow.add_node("invoke_cada_herramienta_dentro_de_etapa_crag_subgraph", invoke_cada_herramienta_dentro_de_etapa_crag_subgraph)
    workflow.add_node("juntar_etapas", juntar_etapas)
    workflow.add_node("invoke_agente_selector_tecnologias", invoke_agente_selector_tecnologias)

    workflow.add_conditional_edges(START, invoke_cada_etapa_tecnologias_posibles, ["invoke_cada_herramienta_dentro_de_etapa_crag_subgraph"])
    workflow.add_edge("invoke_cada_herramienta_dentro_de_etapa_crag_subgraph", "juntar_etapas")
    workflow.add_edge("juntar_etapas", "invoke_agente_selector_tecnologias")
    workflow.add_edge("invoke_agente_selector_tecnologias", END)

    initial_state = State(
        datos_licitacion=datos_licitacion,
        requisitos_etapas=[],
    )

    graph = workflow.compile()
    result = graph.invoke(initial_state)
    print(result)



