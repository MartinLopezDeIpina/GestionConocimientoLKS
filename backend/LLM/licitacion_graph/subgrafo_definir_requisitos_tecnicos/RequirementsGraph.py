import operator
from typing import TypedDict, Annotated

from langchain_core.messages import BaseMessage
from langgraph.constants import Send, START
from langgraph.graph import StateGraph, END

from LLM.licitacion_graph.DatosLicitacion import DatosLicitacion
from LLM.licitacion_graph.modifier_agent import Modificacion
from LLM.licitacion_graph.subgrafo_definir_requisitos_tecnicos.StageRequirementsReactGraph import invoke_requirements_graph_for_stage
from LLM.licitacion_graph.subgrafo_definir_requisitos_tecnicos.StageResult import StageResult


class RequirementsGraphState(TypedDict):
    datos_licitacion: DatosLicitacion
    index_etapa: int
    #operator.add -> cuando se devuelve a la variable del estado, en lugar de reemplazar el valor, se añade a la lista
    stages_results: Annotated[list, operator.add]
    etapas: list[str]

    modificacion_a_realizar: Modificacion
    mensajes_modificacion: list[BaseMessage]


class StageBranchState(TypedDict):
    datos_licitacion: DatosLicitacion
    index_etapa: int
    mensajes_modificacion: list[BaseMessage]


def ejecutar_etapas_node(state: RequirementsGraphState):
    etapas = state["datos_licitacion"].etapas_proyecto
    modificacion_a_realizar = state["modificacion_a_realizar"]

    if modificacion_a_realizar:
        indices = modificacion_a_realizar.index_etapas_a_modificar
        etapas = [etapas[i] for i in indices]

    return {"etapas": etapas}


def continue_to_etapas(state: RequirementsGraphState):
    etapas = state["etapas"]

    return [Send("ejecutar_etapa", {"datos_licitacion": state["datos_licitacion"], "index_etapa": index, "mensajes_modificacion": state["mensajes_modificacion"]}) for index, etapa in enumerate(etapas)]


def ejecutar_etapa(state: StageBranchState):
    index_etapa = state["index_etapa"]
    nombre_etapa = state["datos_licitacion"].etapas_proyecto[index_etapa]
    mensajes_modificacion = state["mensajes_modificacion"]

    result = invoke_requirements_graph_for_stage(state["datos_licitacion"], index_etapa, mensajes_modificacion)
    etapa_result = StageResult(nombre_etapa, index_etapa, result)

    return {"stages_results": [etapa_result]}


def juntar_etapas(state: RequirementsGraphState):
    datos_licitacion = state["datos_licitacion"]
    modificacion_a_realizar = state["modificacion_a_realizar"]

    sorted_results = sorted(state["stages_results"], key=lambda x: x.index_etapa)

    if modificacion_a_realizar:
        for result in sorted_results:
            datos_licitacion.requisitos_etapas[result.index_etapa] = result
    else:
        datos_licitacion.requisitos_etapas = sorted_results

    return {"datos_licitacion": datos_licitacion}


def invoke_requirements_graph(datos_licitacion: DatosLicitacion, modificaciones_a_realizar: Modificacion, modification_messages: list[BaseMessage]):
    initial_state = RequirementsGraphState(
        datos_licitacion=datos_licitacion,
        index_etapa=0,
        etapas=[],
        stages_results=[],
        modificacion_a_realizar=modificaciones_a_realizar,
        mensajes_modificacion=modification_messages
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
    datos_licitacion = result["datos_licitacion"]

    return datos_licitacion
