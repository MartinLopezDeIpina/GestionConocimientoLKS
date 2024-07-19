from typing import TypedDict
import operator
from typing import TypedDict, Annotated, Optional

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_core.tools import tool
from langgraph.constants import Send, START
from langgraph.graph import StateGraph, END
from pydantic import ValidationError
from pydantic.v1 import BaseModel, Field, conlist
from langchain_core.agents import AgentAction

from LLM.LLM_utils import get_tavily_tool, get_tool_name
from LLM.LicitacionGraph import State
from LLM.agents.stageRequirementsReact.ReactAgent import get_react_agent
from LLM.agents.stageRequirementsReact.StageRequirementsReactGraph import invoke_requirements_graph_for_stage


class RequirementsGraphState(TypedDict):
    main_state: State
    index_etapa: int
    stages_results: list[str]
    etapas: list[str]


class StageBranchState(TypedDict):
    main_state: State
    index_etapa: int


class StageResult:
    def __init__(self, etapa: str, index_etapa: int, tecnologias: list[str]):
        self.etapa = etapa
        self.index_etapa = index_etapa
        self.tecnologias = tecnologias


def ejecutar_etapas_node(state: RequirementsGraphState):
    etapas = state["main_state"]["etapas_proyecto"]
    #prueba debug
    return {"etapas": etapas}


def continue_to_etapas(state: RequirementsGraphState):
    etapas = state["main_state"]["etapas_proyecto"]

    return [Send("ejecutar_etapa", {"main_state": state["main_state"], "index_etapa": index}) for index, etapa in enumerate(etapas)]


def ejecutar_etapa(state: StageBranchState):
    index_etapa = state["index_etapa"]
    nombre_etapa = state["main_state"]["etapas_proyecto"][index_etapa]

    result = invoke_requirements_graph_for_stage(state["main_state"], index_etapa)
    etapa_result = StageResult(nombre_etapa, index_etapa, result)

    return {"stages_results": [etapa_result]}


def juntar_etapas(state: RequirementsGraphState):
    return state["stages_results"]


def invoke_requirements_graph(state: State):
    initial_state = RequirementsGraphState(
        main_state=state,
        index_etapa=0,
        stages_results=[],
        etapas=[]
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
    runnable.invoke(initial_state)
