import operator
from typing import TypedDict, Annotated, Optional
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from pydantic.v1 import BaseModel, Field, conlist
from langchain_core.agents import AgentAction
from LLM.licitacion_graph.DatosLicitacion import DatosLicitacion
from LLM.llm_utils.LLM_utils import get_tavily_tool, get_tool_name
from LLM.licitacion_graph.subgrafo_definir_requisitos_tecnicos.ReactAgent import get_react_agent

search = TavilySearchAPIWrapper()
tavily_tool = get_tavily_tool()

MAX_ITERACIONES = 5


class StageRequirementsGraphState(TypedDict):
    datos_licitacion: DatosLicitacion

    etapa_proyecto: str
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]

    iteraciones: int


@tool
def busqueda_tool(pensamiento: str, search_query: str):
    """Busca en la web información relacionada con los requisitos tecnológicos.
    En caso de encontrar implementaciones de tecnologías, el agente considera
    los tipos de tecnologías, no las implementaciones. Por ejemplo, si se encuentra
    necesaria una tecnología como CSS, el agente considerará Herramienta de estilado
    """

    resultados_busqueda = tavily_tool.batch([{"query": search_query}])
    return {"pensamiento": pensamiento, "observacion": resultados_busqueda}


class RequisitosIniciales(BaseModel):
    """Captura inicial de herramientas tecnológicas basándose en la licitación"""
    pensamiento: str = Field(description="Pensamiento del agente al momento de capturar las tecnologías")
    observacion: conlist(str, min_items=2, max_items=5)


class RequisitosModificados(BaseModel):
    """Herramientas tecnológicas modificadas, basándose en la información encontrada en la web
    El agente debe razonar en el pensamiento cuáles herramientas tecnológicas modificar / añadir,
    debe concretar específicamente qué herramientas tecnológicas modificar y por qué
    """
    pensamiento: str = Field(description="Razonamiento de herramientas a modificar / añadir observando el resultado de la búsqueda de qué herramientas tecnológicas modificar")
    observacion: conlist(str, min_items=2, max_items=5) = Field(description="Lista de herramientas tecnológicas tras aplicar las modificaciones")


class RequisitosFinal(BaseModel):
    """Respuesta final de la captura de tecnologías"""
    pensamiento: Optional[str] = Field(description="Pensamiento del agente al finalizar la captura de tecnologías")
    observacion: conlist(str, min_items=2, max_items=5)


tools = [
    busqueda_tool,
    RequisitosIniciales,
    RequisitosModificados,
    RequisitosFinal,
]
tools_final = [RequisitosFinal]

tool_str_to_func = {
    "busqueda_tool": busqueda_tool,
    "RequisitosIniciales": RequisitosIniciales,
    "RequisitosModificados": RequisitosModificados,
    "RequisitosFinal": RequisitosFinal,
}


def run_tool(state: StageRequirementsGraphState):
    tool_name = state["intermediate_steps"][-1].tool
    tool_args = state["intermediate_steps"][-1].tool_input
    # run tool
    if isinstance(tool_str_to_func[tool_name], type):
        # If it's a class, instantiate it with tool_args
        out = tool_str_to_func[tool_name](**tool_args)
    else:
        # If it's a function, invoke it with tool_args
        out = tool_str_to_func[tool_name].invoke(input=tool_args)

    if isinstance(out, dict):
        pensamiento = out['pensamiento']
        observacion = out['observacion']
        state["tecnologias"] = observacion
    else:
        pensamiento = out.pensamiento
        observacion = out.observacion

    log_dict = {
        "pensamiento": pensamiento,
        "observacion": observacion
    }
    action_out = AgentAction(
       tool=tool_name,
       tool_input=log_dict,
       log=str(out)
    )
    return {"intermediate_steps": [action_out]}


def react_agent_node(state: StageRequirementsGraphState):
    iteraciones = state["iteraciones"]
    iteraciones += 1

    # En caso de haberse pasado las iteraciones máximas, devolver siempre la llamada del final
    if iteraciones > MAX_ITERACIONES:
        react_agent = get_react_agent(tools_final)
    else:
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
        "intermediate_steps": [action_out], "iteraciones": iteraciones
    }


def router(state: StageRequirementsGraphState):
    # return the tool name to use
    if isinstance(state["intermediate_steps"], list):
        return state["intermediate_steps"][-1].tool
    else:
        # if we output bad format go to final answer
        print("Router invalid format")
        return "f__class__.__name__inal_requirements_tool"


def invoke_requirements_graph_for_stage(datos_licitacion: DatosLicitacion, etapa_index: int):
    initial_state = StageRequirementsGraphState(
        datos_licitacion=datos_licitacion,
        etapa_proyecto=datos_licitacion.etapas_proyecto[etapa_index],
        intermediate_steps=[],
        iteraciones=0
    )

    graph = StateGraph(StageRequirementsGraphState)

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
    result = runnable.invoke(initial_state)
    return result["intermediate_steps"][-1].tool_input["observacion"]
