import asyncio
import json
from langchain_core.messages import ToolMessage, AIMessage, BaseMessage
from langchain_core.output_parsers import JsonOutputToolsParser
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from collections import defaultdict

from LLM.licitacion_graph.DatosLicitacion import DatosLicitacion
from LLM.licitacion_graph.subgrafo_definir_conocimientos.LATS_tree_model import Node
from LLM.licitacion_graph.subgrafo_definir_conocimientos.TreeState import TreeState
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.subgrafo_generacion_lodo_lats import \
    get_lats_generar_candidatos_runnable
from LLM.llm_utils.LLM_utils import get_tavily_tool, get_model
from LLM.licitacion_graph.subgrafo_definir_conocimientos.LATS_reflection import reflection_chain
from typing import Literal
from langgraph.graph import END, StateGraph, START

candidates_generator = get_lats_generar_candidatos_runnable()
tavily_tool = get_tavily_tool()
tools = [tavily_tool]
tool_executor = ToolExecutor(tools)


def generate_initial_response(state: TreeState) -> dict:
    """Generate the initial candidate response."""
    datos_licitacion = state["datos_licitacion"]
    res = candidates_generator.invoke(
        {
            "datos_licitacion": datos_licitacion,
            "mensajes_feedback": []
        })["datos_licitacion"]
    output_messages = [AIMessage(content=res.get_requisitos_etapas_str())]
    reflection = reflection_chain.invoke(
        {
            "licitacion": datos_licitacion.licitacion,
            "requisitos_adicionales": datos_licitacion.requisitos_adicionales,
            "candidato": output_messages
         }
    )
    root = Node(output_messages, reflection=reflection, candidate_value=res)
    return {
        **state,
        "root": root,
    }


# This generates N candidate values
# for a single input to sample actions from the environment
async def generate_candidates(datos_licitacion: DatosLicitacion, messages: list[BaseMessage], config: RunnableConfig):
    #De default venía a 5
    n = config["configurable"].get("N", 5)

    tasks = [generate_candidate_async(datos_licitacion, messages) for _ in range(n)]
    candidates = await asyncio.gather(*tasks)

    return candidates


async def generate_candidate_async(datos_licitacion: DatosLicitacion, messages: list[BaseMessage]):

    candidate = candidates_generator.invoke(
        {
            "datos_licitacion": datos_licitacion,
            "mensajes_feedback": messages
        }
    )
    return candidate


def expand(state: TreeState, config: RunnableConfig):
    """Starting from the "best" node in the tree, generate N candidates for the next step."""
    root = state["root"]
    best_candidate: Node = root.best_child if root.children else root
    messages = best_candidate.get_trajectory()
    datos_licitacion = state["datos_licitacion"]
    # Generate N candidates from the single child candidate
    # TODO: Ponerle temperatura al llm para que no devuelva siempre lo mismo aquí.h
    # TODO: No funciona concurrencia
    new_candidates = asyncio.run(
        generate_candidates(
            datos_licitacion=datos_licitacion,
            messages=messages,
            config=config,
        )
    )
    new_candidates_messages = [AIMessage(content=c["datos_licitacion"].get_requisitos_etapas_str()) for c in new_candidates]

    # Reflect on each candidate
    # For tasks with external validation, you'd add that here.
    licitacion = datos_licitacion.licitacion
    requisitos_adicionales = datos_licitacion.requisitos_adicionales
    reflections = reflection_chain.batch(
        [{
            "licitacion": licitacion,
            "requisitos_adicionales": requisitos_adicionales,
            "candidato": [msges]
        } for msges in new_candidates_messages],
        config,
    )
    # Grow tree
    child_nodes = [
        Node(cand, parent=best_candidate, reflection=reflection, candidate_value=cand_value)
        for cand, reflection, cand_value in zip(new_candidates_messages, reflections, new_candidates)
    ]
    best_candidate.children.extend(child_nodes)
    # We have already extended the tree directly, so we just return the state
    return state


def should_loop(state: TreeState) -> Literal["expand", "__end__"]:
    """Determine whether to continue the tree search."""
    root = state["root"]
    if root.is_solved:
        return END
    if root.height > 5:
        return END
    return "expand"


def invoke_knowledge_graph(datos_licitacion: DatosLicitacion):
    builder = StateGraph(TreeState)
    builder.add_node("start", generate_initial_response)
    builder.add_node("expand", expand)
    builder.add_edge(START, "start")

    builder.add_conditional_edges(
        "start",
        # Either expand/rollout or finish
        should_loop,
    )
    builder.add_conditional_edges(
        "expand",
        # Either continue to rollout or finish
        should_loop,
    )

    graph = builder.compile()

    last_step = None
    for step in graph.stream({"datos_licitacion": datos_licitacion}):
        last_step = step
        step_name, step_state = next(iter(step.items()))
        print(step_name)
        print("rolled out: ", step_state["root"].height)
        print("---")

    solution_node = last_step["expand"]["root"].get_best_solution()

    return solution_node.candidate_value
