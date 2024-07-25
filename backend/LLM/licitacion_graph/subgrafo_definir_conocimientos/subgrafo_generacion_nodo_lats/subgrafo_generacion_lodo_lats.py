from typing import TypedDict
from langgraph.constants import START, Send
from langgraph.graph import StateGraph
from LLM.licitacion_graph.DatosLicitacion import DatosLicitacion
from LLM.licitacion_graph.subgrafo_definir_requisitos_tecnicos.StageResult import StageResult
from models import NodoArbol


class State(TypedDict):
    datos_licitacion: DatosLicitacion
    tecnologias_posibles: list[NodoArbol]
    index_etapa: int


class StateEtapa(TypedDict):
    requisitos_etapa: StageResult
    index_etapa: int


def invoke_cada_cada_etapa_crag_subgraph(state: State):
    datos_licitacion = state["datos_licitacion"]
    requisitos_etapas = datos_licitacion.requisitos_etapas

    return [Send("invoke_cada_herramienta_dentro_de_etapa_crag_subgraph",
                 {
                        "requisitos_etapa": requisitos_etapa,
                        "index_etapa": index_etapa
                 }) for index_etapa, requisitos_etapa in enumerate(requisitos_etapas)]


def invoke_cada_herramienta_dentro_de_etapa_crag_subgraph(state: StateEtapa):
    requisitos_etapa = state["requisitos_etapa"]

    herramientas_necesarias = requisitos_etapa.tecnologias

    return [Send("invoke_herramienta_crag_subgraph",
                 {
                        "herramienta_necesaria": herramienta_necesaria,
                        "index_herramienta_dentro_de_etapa": index_herramienta_dentro_de_etapa
                 }) for index_herramienta_dentro_de_etapa, herramienta_necesaria in enumerate(herramientas_necesarias)]


def invoke_herramienta_crag_subgraph(state: StateEtapa):
    herramienta_necesaria = state["herramienta_necesaria"]

    #tecnologias_posibles = invoke_tecnologias_posibles_graph(herramienta_necesaria)
    tecnologias_posibles = []

    return {"tecnologias_posibles": [tecnologias_posibles]}


def juntar_tecnologias_de_etapa(state: State):
    sorted_results = sorted(state["tecnologias_posibles"], key=lambda x: x.index_etapa, reverse=True)
    return {"tecnologias_posibles": [sorted_results]}


def invoke_tecnologias_posibles_graph_lats(datos_licitacion: DatosLicitacion):
    workflow = StateGraph(State)

    workflow.add_node("invoke_cada_etapa_crag_subgraph", invoke_cada_cada_etapa_crag_subgraph)
    workflow.add_node("invoke_cada_herramienta_dentro_de_etapa_crag_subgraph", invoke_cada_herramienta_dentro_de_etapa_crag_subgraph)
    workflow.add_node("invoke_herramienta_crag_subgraph", invoke_herramienta_crag_subgraph)
    workflow.add_node("juntar_tecnologias_de_etapa", juntar_tecnologias_de_etapa)

    workflow.add_edge(START, "invoke_cada_etapa_crag_subgraph")
    workflow.add_edge("invoke_cada_etapa_crag_subgraph", "invoke_cada_herramienta_dentro_de_etapa_crag_subgraph")
    workflow.add_edge("invoke_cada_herramienta_dentro_de_etapa_crag_subgraph", "invoke_herramienta_crag_subgraph" )
    workflow.add_edge("invoke_herramienta_crag_subgraph", "juntar_tecnologias_de_etapa")

    initial_state = State(
        datos_licitacion=datos_licitacion,
        tecnologias_posibles=[],
        index_etapa=0,
        index_herramienta_dentro_de_etapa=0
    )

    graph = workflow.compile()
    result = graph.invoke(initial_state)
    print(result)



