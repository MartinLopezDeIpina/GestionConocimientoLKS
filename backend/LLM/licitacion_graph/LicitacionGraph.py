import asyncio
import uuid

from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langgraph.checkpoint import MemorySaver
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

from LLM.licitacion_graph.DatosLicitacion import DatosLicitacion
from LLM.licitacion_graph.modifier_agent import invoke_modificar_propuesta, Modificacion
from LLM.licitacion_graph.subgrafo_categorizar_proyecto.AgenteCategorizadorProyectos import \
    get_proyect_definer_agetn_run_output
from LLM.licitacion_graph.subgrafo_definir_conocimientos.LATS_define_kwoledge_graph import invoke_knowledge_graph
from LLM.licitacion_graph.subgrafo_definir_requisitos_tecnicos.RequirementsGraph import invoke_requirements_graph, \
    StageResult
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesCustomReflection.StagesReflectionGraph import \
    invoke_stages_sub_graph_and_get_proposed_stages


class State(TypedDict):
    datos_licitacion: DatosLicitacion
    feedback: str
    modificacion_a_realizar: Modificacion
    mensajes: list[BaseMessage]


def invoke_proyect_definer_model(state: State):
    datos_licitacion = state["datos_licitacion"]
    mensajes = state["mensajes"]

    categoria_proyecto = get_proyect_definer_agetn_run_output(datos_licitacion, mensajes)

    datos_licitacion.categoria_proyecto = categoria_proyecto

    return {"datos_licitacion": datos_licitacion, "modificacion_a_realizar": None}


def invoke_proyect_stages_subgraph(state: State):
    datos_licitacion = state["datos_licitacion"]

    proposed_steps = invoke_stages_sub_graph_and_get_proposed_stages(datos_licitacion)

    datos_licitacion.etapas_proyecto = proposed_steps
    return {"datos_licitacion": datos_licitacion}


def invoke_proyect_tools_subgraph(state: State):
    datos_licitacion = state["datos_licitacion"]
    modificacion_a_realizar = state["modificacion_a_realizar"]
    mensajes = state["mensajes"]

    datos_licitacion = invoke_requirements_graph(datos_licitacion, modificacion_a_realizar, mensajes)

    return {"datos_licitacion": datos_licitacion, "modificacion_a_realizar": None}


def invoke_lats_subgrafo_definir_conocimientos(state: State):
    datos_licitacion = state["datos_licitacion"]
    modificacion_a_realizar = state["modificacion_a_realizar"]
    mensajes = state["mensajes"]

    proyecto = invoke_knowledge_graph(datos_licitacion, modificacion_a_realizar, mensajes)

    return {"datos_licitacion": proyecto, "modificacion_a_realizar": None}


# Para poner el breakpoint delante
def input_humano_proyecto_valido(state: State):
    pass


def invoke_proyect_modifier_graph(state: State):
    datos_licitacion = state["datos_licitacion"]
    requisitos_adicionales = datos_licitacion.requisitos_adicionales
    propuesta_proyecto_str = datos_licitacion.get_requisitos_etapas_str()
    feedback = state["feedback"]
    mensajes = state["mensajes"]

    mensajes.append(AIMessage(content=propuesta_proyecto_str))
    mensajes.append(HumanMessage(content=feedback))

    requisitos_adicionales.append(feedback)

    modificacion_a_realizar = invoke_modificar_propuesta(datos_licitacion, feedback)

    return {"modificacion_a_realizar": modificacion_a_realizar, "mensajes": mensajes,
            "datos_licitacion": datos_licitacion}


def conditional_modificacion_a_realizar(state: State):
    modificacion_a_realizar = state["modificacion_a_realizar"]

    if modificacion_a_realizar.sugrafo_a_llamar == "INICIAL":
        return "proyect_definer_model"
    elif modificacion_a_realizar.sugrafo_a_llamar == "DEFINIR_HERRAMIENTAS_DE_ETAPAS":
        return "proyect_tools_subgraph"
    elif modificacion_a_realizar.sugrafo_a_llamar == "DEFINIR_CONOCIMIENTOS":
        return "lats_subgrafo_definir_conocimientos"


async def start_licitacion_graph(licitacion, requisitos_adicionales):
    workflow = StateGraph(State)

    workflow.add_node("proyect_definer_model", invoke_proyect_definer_model)
    workflow.add_node("proyect_stages_subgraph", invoke_proyect_stages_subgraph)
    workflow.add_node("proyect_tools_subgraph", invoke_proyect_tools_subgraph)
    workflow.add_node("lats_subgrafo_definir_conocimientos", invoke_lats_subgrafo_definir_conocimientos)
    workflow.add_node("nodo_proyecto_valido", input_humano_proyecto_valido)
    workflow.add_node("invoke_proyect_modifier_graph", invoke_proyect_modifier_graph)

    workflow.add_edge(START, "proyect_definer_model")
    workflow.add_edge("proyect_definer_model", "proyect_stages_subgraph")
    workflow.add_edge("proyect_stages_subgraph", "proyect_tools_subgraph")
    workflow.add_edge("proyect_tools_subgraph", "lats_subgrafo_definir_conocimientos")
    workflow.add_edge("lats_subgrafo_definir_conocimientos", "nodo_proyecto_valido")
    workflow.add_edge("nodo_proyecto_valido", "invoke_proyect_modifier_graph")
    workflow.add_conditional_edges("invoke_proyect_modifier_graph", conditional_modificacion_a_realizar)

    initial_state = State(
        datos_licitacion=DatosLicitacion(
            licitacion=licitacion,
            categoria_proyecto="",
            requisitos_adicionales=requisitos_adicionales,
            requisitos_etapas=[],
            etapas_proyecto=[],
        ),
        feedback="",
        modificacion_a_realizar=None,
        mensajes=[],
    )

    memory = MemorySaver()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {
        "thread_id": thread_id
    }}

    graph = workflow.compile(checkpointer=memory, interrupt_before=["nodo_proyecto_valido"])

    result = None

    while True:
        # Si se ejecuta el grafo por primera vez (no ha habido ningún human-in-the-loop) pasarle el initial state
        graph_result = graph.invoke(initial_state if not result else None, config=config)
        result = graph_result["datos_licitacion"]

        print(f"Se ha obtenido el siguiente resultado: \n{result.get_requisitos_etapas_str()}\n\n")

        input_valida = input("¿Es una propuesta válida? (s/n): ")
        propuesta_valida = input_valida.lower() in ["s", "si"]

        if propuesta_valida:
            break

        feedback = input("¿Qué cambios se deben realizar?: ")

        updated_state = {
            "datos_licitacion": result,
            "feedback": feedback,
            "modificacion_a_realizar": None,
            "mensajes": graph_result["mensajes"]
        }

        graph.update_state(config=config, values=updated_state)

    return result


def test_start_licitacion_graph(licitacion, requisitos_adicionales):
    asyncio.run(start_licitacion_graph(licitacion=licitacion, requisitos_adicionales=requisitos_adicionales))
