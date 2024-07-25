import asyncio

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

from LLM.licitacion_graph.DatosLicitacion import DatosLicitacion
from LLM.licitacion_graph.subgrafo_categorizar_proyecto.AgenteCategorizadorProyectos import get_proyect_definer_agetn_run_output
from LLM.licitacion_graph.subgrafo_definir_conocimientos.LATS_define_kwoledge_graph import invoke_knowledge_graph
from LLM.licitacion_graph.subgrafo_definir_requisitos_tecnicos.RequirementsGraph import invoke_requirements_graph, StageResult
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesCustomReflection.StagesReflectionGraph import invoke_stages_sub_graph_and_get_proposed_stages


class State(TypedDict):
    licitacion: str
    requisitos_adicionales: list[str]

    categoria_proyecto: str
    etapas_proyecto: list[str]
    requisitos_etapas: list[StageResult]


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
    datos_licitacion = DatosLicitacion(
        licitacion=state["licitacion"],
        requisitos_adicionales=state["requisitos_adicionales"],
        categoria_proyecto=state["categoria_proyecto"],
        etapas_proyecto=state["etapas_proyecto"]
    )
    steps_results = invoke_requirements_graph(datos_licitacion)
    return {"requisitos_etapas": steps_results}


def invoke_lats_subgrafo_definir_conocimientos(state: State):
    datos_licitacion = state["datos_licitacion"]

    proyecto = invoke_knowledge_graph(datos_licitacion)

async def start_licitacion_graph(licitacion, requisitos_adicionales):
    workflow = StateGraph(State)

    workflow.add_node("proyect_definer_model", invoke_proyect_definer_model)
    workflow.add_node("proyect_stages_subgraph", invoke_proyect_stages_subgraph)
    workflow.add_node("proyect_tools_subgraph", invoke_proyect_tools_subgraph)
    workflow.add_node("lats_subgrafo_definir_conocimientos", invoke_lats_subgrafo_definir_conocimientos)

    workflow.add_edge(START, "proyect_definer_model")
    workflow.add_edge("proyect_definer_model", "proyect_stages_subgraph")
    workflow.add_edge("proyect_stages_subgraph", "proyect_tools_subgraph")
    workflow.add_edge("proyect_tools_subgraph", "lats_subgrafo_definir_conocimientos")
    workflow.add_edge("lats_subgrafo_definir_conocimientos", END)

    initial_state = State(licitacion=licitacion, requisitos_adicionales=requisitos_adicionales, categoria_proyecto=""
                          , etapas_proyecto=[], requisitos_etapas=[])

    graph = workflow.compile()

    async for output in graph.astream(initial_state, stream_mode="values"):
        print(output)


def test_start_licitacion_graph(licitacion, requisitos_adicionales):
    asyncio.run(start_licitacion_graph(licitacion, requisitos_adicionales))

