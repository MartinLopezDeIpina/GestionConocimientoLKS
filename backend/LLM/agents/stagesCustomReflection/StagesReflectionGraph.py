import asyncio
from langgraph.graph import END, START, StateGraph

from LLM.agents.stagesCustomReflection.AnswerQuestion import AnswerQuestion
from LLM.agents.stagesCustomReflection.EtapasProyecto import EtapasProyecto
from LLM.agents.stagesCustomReflection.StagesResponderAgent import get_initial_generador, get_generador
from LLM.agents.stagesCustomReflection.Reflection import Reflection
from LLM.agents.stagesCustomReflection.StagesRevisorAgent import get_revisor
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

from LLM.agents.stagesCustomReflection.State import State

MAX_ITERATIONS = 3

search = TavilySearchAPIWrapper()
tavily_tool = TavilySearchResults(api_wrapper=search, max_results=5)


def run_queries(search_queries: list[str], **kwargs):
    """Run the generated queries."""
    return tavily_tool.batch([{"query": query} for query in search_queries])


def tool_node(state: State):
    # Incrementar el número de iteraciones
    num_iteraciones = state["num_iteraciones"]
    num_iteraciones += 1

    resultados_busqueda = run_queries(state["critica_actual"].search_queries)
    return {"resultados_busqueda": resultados_busqueda, "num_iteraciones": num_iteraciones}


def event_loop(state: State):
    # in our case, we'll just stop after N plans
    num_iterations = state["num_iteraciones"]
    if num_iterations >= MAX_ITERATIONS:
        return END
    return "revise"


def revisor_node(state: State):
    licitacion = state["licitacion"]
    requisitos_adicionales = state["requisitos_adicionales"]
    categoria_proyecto = state["categoria_proyecto"]
    propuesta_etapas = state["propuesta_etapas"]
    validacion_error = state["validation_error"]

    revisor = get_revisor(licitacion, requisitos_adicionales, categoria_proyecto, propuesta_etapas, validacion_error)
    result = revisor.respond(state)

    return result


def start_stages_custom_reflection_graph(licitacion, requisitos_adicionales, categoria_proyecto):
    asyncio.run(invoke_stages_sub_graph_and_get_proposed_stages(licitacion, requisitos_adicionales, categoria_proyecto))


def initial_generator_node(state: State):
    licitacion = state["licitacion"]
    requisitos_adicionales = state["requisitos_adicionales"]
    categoria_proyecto = state["categoria_proyecto"]

    generador = get_initial_generador(licitacion, requisitos_adicionales, categoria_proyecto)
    propuesta_etapas = generador.invoke({})
    return {"propuesta_etapas": propuesta_etapas}


def generator_node(state: State):
    licitacion = state["licitacion"]
    requisitos_adicionales = state["requisitos_adicionales"]
    categoria_proyecto = state["categoria_proyecto"]
    propuesta_etapas = state["propuesta_etapas"]
    critica_actual = state["critica_actual"]
    resultados_busqueda = state["resultados_busqueda"]

    generador = get_generador(licitacion, requisitos_adicionales, categoria_proyecto, propuesta_etapas, critica_actual, resultados_busqueda)
    propuesta_etapas = generador.invoke({})
    return {"propuesta_etapas": propuesta_etapas}


def invoke_stages_sub_graph_and_get_proposed_stages(licitacion, requisitos_adicionales, categoria_proyecto):
    builder = StateGraph(State)

    builder.add_node("draft", initial_generator_node)
    builder.add_node("generator", generator_node)
    builder.add_node("execute_tools", tool_node)
    builder.add_node("revise", revisor_node)

    builder.add_edge("draft", "revise")
    builder.add_edge("revise", "execute_tools")
    builder.add_edge("execute_tools", "generator")
    builder.add_conditional_edges("generator", event_loop)
    builder.add_edge(START, "draft")

    graph = builder.compile()

    initial_state = State(
        licitacion=licitacion,
        requisitos_adicionales=requisitos_adicionales,
        categoria_proyecto=categoria_proyecto,
        critica_actual=AnswerQuestion(
            reflexion=Reflection(falta="", sobra=""),
            search_queries=[],
        ),
        resultados_busqueda="",
        num_iteraciones=0,
        propuesta_etapas=EtapasProyecto(explicacion="", etapas=[], referencias=[]),
        validation_error="",
    )

    output = graph.invoke(initial_state)
    etapas_proyecto = output["propuesta_etapas"]
    etapas = etapas_proyecto.etapas

    return etapas


