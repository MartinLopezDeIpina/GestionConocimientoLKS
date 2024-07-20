import operator
from typing import TypedDict, Annotated
from langgraph.constants import Send, START
from langgraph.graph import StateGraph, END

from LLM.DatosLicitacion import DatosLicitacion
from LLM.agents.stageRequirementsReact.StageRequirementsReactGraph import invoke_requirements_graph_for_stage
from LLM.agents.stageRequirementsReact.StageResult import StageResult


class RequirementsGraphState(TypedDict):
    datos_licitacion: DatosLicitacion
    index_etapa: int
    #operator.add -> cuando se devuelve a la variable del estado, en lugar de reemplazar el valor, se añade a la lista
    stages_results: Annotated[list, operator.add]
    sorted_final_results: list[StageResult]
    etapas: list[str]


class StageBranchState(TypedDict):
    datos_licitacion: DatosLicitacion
    index_etapa: int


def ejecutar_etapas_node(state: RequirementsGraphState):
    etapas = state["datos_licitacion"].etapas_proyecto
    return {"etapas": etapas}


def continue_to_etapas(state: RequirementsGraphState):
    etapas = state["etapas"]

    return [Send("ejecutar_etapa", {"datos_licitacion": state["datos_licitacion"], "index_etapa": index}) for index, etapa in enumerate(etapas)]


def ejecutar_etapa(state: StageBranchState):
    index_etapa = state["index_etapa"]
    nombre_etapa = state["datos_licitacion"].etapas_proyecto[index_etapa]

    result = invoke_requirements_graph_for_stage(state["datos_licitacion"], index_etapa)
    etapa_result = StageResult(nombre_etapa, index_etapa, result)

    return {"stages_results": [etapa_result]}


def juntar_etapas(state: RequirementsGraphState):
    sorted_results = sorted(state["stages_results"], key=lambda x: x.index_etapa)
    return {"sorted_final_results": sorted_results}


def invoke_requirements_graph(datos_licitacion: DatosLicitacion):
    initial_state = RequirementsGraphState(
        datos_licitacion=datos_licitacion,
        index_etapa=0,
        etapas=[],
        stages_results=[],
        sorted_final_results=[]
    )

    graph = StateGraph(RequirementsGraphState)

    graph.add_node("ejecutar_etapas", ejecutar_etapas_node)
    graph.add_node("ejecutar_etapa", ejecutar_etapa)
    graph.add_node("juntar_etapas", juntar_etapas)

    graph.add_edge(START, "ejecutar_etapas")
    #Crear edge dinámica, se especifica en el Send la cantidad de nodos que se van a llamar
    graph.add_conditional_edges("ejecutar_etapas", continue_to_etapas, ["ejecutar_etapa"])
    graph.add_edge("ejecutar_etapa", "juntar_etapas")
    graph.add_edge("juntar_etapas", END)

    runnable = graph.compile()
    result = runnable.invoke(initial_state)
    stages_results = result["sorted_final_results"]

    for stage_result in stages_results:
        print(stage_result)

    return stages_results
