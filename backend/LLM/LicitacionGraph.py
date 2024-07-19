import operator
from typing import Annotated, Any

import asyncio

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

import utils
from LLM.agents.AgenteCategorizadorProyectos import get_proyect_definer_agetn_run_output
from LLM.agents.stagesCustomReflection.StagesReflectionGraph import invoke_stages_sub_graph_and_get_proposed_stages


class State(TypedDict):
    licitacion: str
    requisitos_adicionales: list[str]

    categoria_proyecto: str
    etapas_proyecto: list[str]


def invoke_proyect_definer_model(state: State):
    licitacion = state["licitacion"]
    requisitos_adicionales = state["requisitos_adicionales"]

    resultado = get_proyect_definer_agetn_run_output(licitacion, requisitos_adicionales)
    return {"categoria_proyecto": resultado}


def invoke_proyect_stages_subgraph(state: State):
    licitacion = state["licitacion"]
    requisitos_adicionales = state["requisitos_adicionales"]
    categoria_proyecto = state["categoria_proyecto"]

    proposed_steps = invoke_stages_sub_graph_and_get_proposed_stages(licitacion, requisitos_adicionales, categoria_proyecto)
    return {"etapas_proyecto": proposed_steps}


def invoke_proyect_tools_subgraph(state: State):
    pass


async def start_licitacion_graph(licitacion, requisitos_adicionales):
    workflow = StateGraph(State)

    workflow.add_node("proyect_definer_model", invoke_proyect_definer_model)
    workflow.add_node("proyect_stages_subgraph", invoke_proyect_stages_subgraph)

    workflow.add_edge(START, "proyect_definer_model")
    workflow.add_edge("proyect_definer_model", "proyect_stages_subgraph")
    workflow.add_edge("proyect_stages_subgraph", END)

    initial_state = State(licitacion=licitacion, requisitos_adicionales=requisitos_adicionales, categoria_proyecto=""
                          , etapas_proyecto=[])

    graph = workflow.compile()

    async for output in graph.astream(initial_state, stream_mode="values"):
        print(output)


def test_start_licitacion_graph(licitacion, requisitos_adicionales):
    asyncio.run(start_licitacion_graph(licitacion, requisitos_adicionales))

