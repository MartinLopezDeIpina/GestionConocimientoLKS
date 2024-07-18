import operator
from typing import TypedDict, Annotated

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from pydantic.v1 import BaseModel
from langchain_core.agents import AgentAction

from LLM.LLM_utils import get_tavily_tool, get_tool_name
from LLM.LicitacionGraph import State
from LLM.agents.stageRequirementsReact.ReactAgent import get_react_agent

search = TavilySearchAPIWrapper()
tavily_tool = get_tavily_tool()


class RequirementsGraphState(TypedDict):
    main_state: State

    etapa_proyecto: str
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]


@tool
def busqueda_tool(search_query: str) -> list[str]:
    """Busca en la web información relacionada con los requisitos"""

    resultados_busqueda = tavily_tool.batch([{"query": search_query}])
    return resultados_busqueda


class RequisitosIniciales(BaseModel):
    """Requisitos técnicos iniciales de la captura de requisitos basándose en la licitación"""
    requisitos: list[str]


class RequisitosModificados(BaseModel):
    """Requisitos técnicos modificados de la captura de requisitos basándose en la información encontrada en la web"""
    modificaciones: list[str]
    requisitos: list[str]


class RequisitosFinal(BaseModel):
    """Respuesta final de la captura de requisitos"""
    requisitos: list[str]


tools = [
    busqueda_tool,
    RequisitosIniciales,
    RequisitosModificados,
    RequisitosFinal,
]


tool_str_to_func = {
    "busqueda_tool": busqueda_tool,
    "RequisitosIniciales": RequisitosIniciales,
    "RequisitosModificados": RequisitosModificados,
    "RequisitosFinal": RequisitosFinal,
}


def run_tool(state: RequirementsGraphState):
    tool_name = state["intermediate_steps"][-1].tool
    tool_args = state["intermediate_steps"][-1].tool_input
    print(f"{tool_name}.invoke(input={tool_args})")
    # run tool
    if isinstance(tool_str_to_func[tool_name], type):
        # If it's a class, instantiate it with tool_args
        out = tool_str_to_func[tool_name](**tool_args)
    else:
        # If it's a function, invoke it with tool_args
        out = tool_str_to_func[tool_name].invoke(input=tool_args)
    action_out = AgentAction(
       tool=tool_name,
       tool_input=tool_args,
       log=str(out)
    )
    return {"intermediate_steps": [action_out]}


def react_agent_node(state: RequirementsGraphState):
    react_agent = get_react_agent(tools)

    out = react_agent.invoke(state)

    tool_name = out.tool_calls[0]["name"]
    tool_args = out.tool_calls[0]["args"]
    action_out = AgentAction(
        tool=tool_name,
        tool_input=tool_args,
        log="TBD"
    )

    return {
        "intermediate_steps": [action_out]
    }


def router(state: RequirementsGraphState):
    # return the tool name to use
    if isinstance(state["intermediate_steps"], list):
        return state["intermediate_steps"][-1].tool
    else:
        # if we output bad format go to final answer
        print("Router invalid format")
        return "f__class__.__name__inal_requirements_tool"


def invoke_requirements_graph(state: State, etapa_index: int):
    initial_state = RequirementsGraphState(
        main_state=state,
        etapa_proyecto=state["etapas_proyecto"][etapa_index],
        intermediate_steps=[]
    )

    graph = StateGraph(RequirementsGraphState)

    graph.add_node("react_agent", react_agent_node)
    graph.add_node("busqueda_tool", run_tool)
    graph.add_node("RequisitosIniciales", run_tool)
    graph.add_node("RequisitosModificados", run_tool)
    graph.add_node("RequisitosFinal", run_tool)

    graph.set_entry_point("react_agent")
    graph.add_conditional_edges(source="react_agent", path=router)

    # create edges from each tool back to the oracle
    for tool_obj in tools:
        tool_name = get_tool_name(tool_obj)
        if tool_name != "RequisitosFinal":
            graph.add_edge(tool_name, "react_agent")

    graph.add_edge("RequisitosFinal", END)

    runnable = graph.compile()
    runnable.invoke(initial_state)
