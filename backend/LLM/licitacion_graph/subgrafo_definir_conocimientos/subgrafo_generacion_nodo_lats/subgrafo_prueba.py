import operator
from typing import TypedDict, Annotated
from langgraph.constants import START, END, Send
from langgraph.graph import StateGraph
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.subgrafo_prueba_herramientas.subgrafo_prueba_herramientas import \
    invoke_subgrafo_prueba_herramientas


class StateEtapa(TypedDict):
    nombre_etapa: str
    index_etapa: int
    result: str


class State(TypedDict):
    etapas: list[str]
    resultados_etapas: Annotated[list[StateEtapa], operator.add]


def invoke_etapas(state: State):
    etapas = state["etapas"]

    return [Send("ejecutar_etapa",
                 {
                        "nombre_etapa": etapa,
                        "index_etapa": index_etapa
                 }) for index_etapa, etapa in enumerate(etapas)]


def ejecutar_etapa(state: StateEtapa):
    nombre_etapa = state["nombre_etapa"]
    index_etapa = state["index_etapa"]

    result_herramientas = invoke_subgrafo_prueba_herramientas(
        [f"{nombre_etapa}_herramienta1",
         f"{nombre_etapa}_herramienta2",
         f"{nombre_etapa}_herramienta3"])
    result = f"resultado de etapa {nombre_etapa} con index {index_etapa} es {result_herramientas}"

    state["result"] = result

    return {"resultados_etapas": [state]}


def juntar_etapas(state: State):
    sorted_results = sorted(state["resultados_etapas"], key=lambda x: x["index_etapa"], reverse=True)
    return {"resultados_etapas": [sorted_results]}


def printear_resultados_etapas(state: State):
    for result in state["resultados_etapas"]:
        print(result)


def invoke_subgrafo_prueba():
    workflow = StateGraph(State)

    workflow.add_node("ejecutar_etapa", ejecutar_etapa)
    workflow.add_node("juntar_etapas", juntar_etapas)
    workflow.add_node("printear_resultados_etapas", printear_resultados_etapas)

    workflow.add_conditional_edges(START, invoke_etapas, ["ejecutar_etapa"])
    workflow.add_edge("ejecutar_etapa", "juntar_etapas")
    workflow.add_edge("juntar_etapas", "printear_resultados_etapas")
    workflow.add_edge("printear_resultados_etapas", END)

    initial_state = State(
        etapas=["etapa1", "etapa2", "etapa3"],
        resultados_etapas=[],
    )

    graph = workflow.compile()
    result = graph.invoke(initial_state)
    print(result["resultados_etapas"])



