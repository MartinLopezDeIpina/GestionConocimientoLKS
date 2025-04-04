import asyncio
from langgraph.graph import END, START, StateGraph

from LLM.licitacion_graph.subgrafo_definir_etapas.stagesReflection.Reflection import Reflection
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesReflection.StagesResponderAgent import get_first_responder, AnswerQuestion
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesReflection.StagesRevisorAgent import get_revisor

from LLM.licitacion_graph.subgrafo_definir_etapas.stagesReflection.State import State
from LLM.llm_utils import LLM_utils

MAX_ITERATIONS = 3

tavily_tool = LLM_utils.get_tavily_tool()


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
    return "execute_tools"


def revisor_node(state: State):
    licitacion = state["licitacion"]
    requisitos_adicionales = state["requisitos_adicionales"]
    categoria_proyecto = state["categoria_proyecto"]
    critica_actual = state["critica_actual"]
    resultados_busqueda = state["resultados_busqueda"]

    revisor = get_revisor(licitacion, requisitos_adicionales, categoria_proyecto, critica_actual, resultados_busqueda)
    result = revisor.respond(state)

    return result


def start_stages_reflection_graph(licitacion, requisitos_adicionales, categoria_proyecto):
    asyncio.run(start_stages_reflection_graph_async(licitacion, requisitos_adicionales, categoria_proyecto))


async def start_stages_reflection_graph_async(licitacion, requisitos_adicionales, categoria_proyecto):
    first_responder = get_first_responder(licitacion, requisitos_adicionales, categoria_proyecto)

    builder = StateGraph(State)

    builder.add_node("draft", first_responder.respond)
    builder.add_node("execute_tools", tool_node)
    builder.add_node("revise", revisor_node)

    builder.add_edge("draft", "execute_tools")
    builder.add_edge("execute_tools", "revise")

    # revise -> execute_tools OR end
    builder.add_conditional_edges("revise", event_loop)
    builder.add_edge(START, "draft")
    graph = builder.compile()

    initial_state = State(
        licitacion=licitacion,
        requisitos_adicionales=requisitos_adicionales,
        categoria_proyecto=categoria_proyecto,
        critica_actual=AnswerQuestion(
            etapas=[],
            reflexion=Reflection(falta="", sobra=""),
            search_queries=[],
        ),
        resultados_busqueda="",
        num_iteraciones=0
    )

    async for output in graph.astream(initial_state, stream_mode="values"):
        print(output)

