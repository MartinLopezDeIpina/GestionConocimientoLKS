import operator
from typing import typeddict, annotated, optional
from langchain_community.utilities.tavily_search import tavilysearchapiwrapper
from langchain_core.tools import tool
from langgraph.graph import stategraph, end
from pydantic.v1 import basemodel, field, conlist
from langchain_core.agents import agentaction
from llm.licitacion_graph.datoslicitacion import datoslicitacion
from llm.llm_utils.llm_utils import get_tavily_tool, get_tool_name
from llm.licitacion_graph.subgrafo_definir_requisitos_tecnicos.reactagent import get_react_agent

search = tavilysearchapiwrapper()
tavily_tool = get_tavily_tool()

max_iteraciones = 5


class stagerequirementsgraphstate(typeddict):
    datos_licitacion: datoslicitacion

    etapa_proyecto: str
    intermediate_steps: annotated[list[tuple[agentaction, str]], operator.add]

    iteraciones: int


@tool
def busqueda_tool(pensamiento: str, search_query: str):
    """busca en la web información relacionada con los requisitos tecnológicos.
    en caso de encontrar implementaciones de tecnologías, el agente considera
    los tipos de tecnologías, no las implementaciones. por ejemplo, si se encuentra
    necesaria una tecnología como css, el agente considerará herramienta de estilado
    """

    resultados_busqueda = tavily_tool.batch([{"query": search_query}])
    return {"pensamiento": pensamiento, "observacion": resultados_busqueda}


class requisitosiniciales(basemodel):
    """captura inicial de herramientas tecnológicas basándose en la licitación"""
    pensamiento: str = field(description="pensamiento del agente al momento de capturar las tecnologías")
    observacion: conlist(str, min_items=2, max_items=5)


class requisitosmodificados(basemodel):
    """herramientas tecnológicas modificadas, basándose en la información encontrada en la web
    el agente debe razonar en el pensamiento cuáles herramientas tecnológicas modificar / añadir,
    debe concretar específicamente qué herramientas tecnológicas modificar y por qué
    """
    pensamiento: str = field(description="razonamiento de herramientas a modificar / añadir observando el resultado de la búsqueda de qué herramientas tecnológicas modificar")
    observacion: conlist(str, min_items=2, max_items=5) = field(description="lista de herramientas tecnológicas tras aplicar las modificaciones")


class requisitosfinal(basemodel):
    """respuesta final de la captura de tecnologías"""
    pensamiento: optional[str] = field(description="pensamiento del agente al finalizar la captura de tecnologías")
    observacion: conlist(str, min_items=2, max_items=5)


tools = [
    busqueda_tool,
    requisitosiniciales,
    requisitosmodificados,
    requisitosfinal,
]
tools_final = [requisitosfinal]

tool_str_to_func = {
    "busqueda_tool": busqueda_tool,
    "requisitosiniciales": requisitosiniciales,
    "requisitosmodificados": requisitosmodificados,
    "requisitosfinal": requisitosfinal,
}


def run_tool(state: stagerequirementsgraphstate):
    tool_name = state["intermediate_steps"][-1].tool
    tool_args = state["intermediate_steps"][-1].tool_input
    # run tool
    if isinstance(tool_str_to_func[tool_name], type):
        # if it's a class, instantiate it with tool_args
        out = tool_str_to_func[tool_name](**tool_args)
    else:
        # if it's a function, invoke it with tool_args
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
    action_out = agentaction(
       tool=tool_name,
       tool_input=log_dict,
       log=str(out)
    )
    return {"intermediate_steps": [action_out]}


def react_agent_node(state: stagerequirementsgraphstate):
    iteraciones = state["iteraciones"]
    iteraciones += 1

    # en caso de haberse pasado las iteraciones máximas, devolver siempre la llamada del final
    if iteraciones > max_iteraciones:
        react_agent = get_react_agent(tools_final)
    else:
        react_agent = get_react_agent(tools)

    out = react_agent.invoke(state)

    tool_name = out.tool_calls[0]["name"]
    tool_args = out.tool_calls[0]["args"]
    action_out = agentaction(
        tool=tool_name,
        tool_input=tool_args,
        log="tbd"
    )

    return {
        "intermediate_steps": [action_out], "iteraciones": iteraciones
    }


def router(state: stagerequirementsgraphstate):
    # return the tool name to use
    if isinstance(state["intermediate_steps"], list):
        return state["intermediate_steps"][-1].tool
    else:
        # if we output bad format go to final answer
        print("router invalid format")
        return "f__class__.__name__inal_requirements_tool"


def invoke_requirements_graph_for_stage(datos_licitacion: datoslicitacion, etapa_index: int):
    initial_state = stagerequirementsgraphstate(
        datos_licitacion=datos_licitacion,
        etapa_proyecto=datos_licitacion.etapas_proyecto[etapa_index],
        intermediate_steps=[],
        iteraciones=0
    )

    graph = stategraph(stagerequirementsgraphstate)

    graph.add_node("react_agent", react_agent_node)
    graph.add_node("busqueda_tool", run_tool)
    graph.add_node("requisitosiniciales", run_tool)
    graph.add_node("requisitosmodificados", run_tool)
    graph.add_node("requisitosfinal", run_tool)

    graph.set_entry_point("react_agent")
    graph.add_conditional_edges(source="react_agent", path=router)

    # create edges from each tool back to the oracle
    for tool_obj in tools:
        tool_name = get_tool_name(tool_obj)
        if tool_name != "requisitosfinal":
            graph.add_edge(tool_name, "react_agent")

    graph.add_edge("requisitosfinal", end)

    runnable = graph.compile()
    result = runnable.invoke(initial_state)
    return result["intermediate_steps"][-1].tool_input["observacion"]
