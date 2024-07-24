import uuid
from typing import TypedDict

from langgraph.checkpoint import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_tecnologias_posibles.subgrafo_proponer_tecnologia_nuevas.Buscar_nodo_padre_agent import \
    invoke_buscar_nodo_padre_agent
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_tecnologias_posibles.subgrafo_proponer_tecnologia_nuevas.Proposer_agent import \
    invoke_proposer_get_tecnologia_propuesta
from database import db
from models import NodoArbol, RelacionesNodo


class State(TypedDict):
    herramienta_necesaria: str
    tecnologias_rechazadas: list[NodoArbol]

    anadir_tecnologia_al_arbol: bool
    tecnologia_propuesta: str
    nodo_padre_id: int
    nodo_anadido: NodoArbol


def invoke_proposer_agent(state: State):
    herramienta_necesaria = state["herramienta_necesaria"]
    tecnologias_rechazadas = state["tecnologias_rechazadas"]

    tecnologia_propuesta = invoke_proposer_get_tecnologia_propuesta(herramienta_necesaria, tecnologias_rechazadas)
    return {"tecnologia_propuesta": tecnologia_propuesta}


def invoke_buscador_de_padre_agent(state: State):
    tecnologia_propuesta = state["tecnologia_propuesta"]

    nodo_padre_id = invoke_buscar_nodo_padre_agent(tecnologia_propuesta)
    return {"nodo_padre_id": nodo_padre_id}


def anadir_nodo_al_arbol(state: State):
    nodo_padre_id = state["nodo_padre_id"]
    tecnologia_propuesta = state["tecnologia_propuesta"]

    nodo_anadido = NodoArbol(nombre=tecnologia_propuesta)
    db.session.add(nodo_anadido)
    db.session.commit()

    relacion_padre_hijo = RelacionesNodo(ascendente_id=nodo_padre_id, descendente_id=nodo_anadido.nodoID)
    db.session.add(relacion_padre_hijo)
    db.session.commit()

    return {"nodo_anadido": nodo_anadido}


def get_input_humano(state: State):
    pass


def conditional_anadir_tecnologia_al_arbol(state: State):
    anadir_nodo_al_arbol = state["anadir_tecnologia_al_arbol"]

    if anadir_nodo_al_arbol:
        return "buscar_nodo_padre"
    else:
        return END


def invoke_subgrafo_proponer_tecnologia_nueva(herramienta_necesaria: str, tecnologias_rechazadas: list[NodoArbol]):
    workflow = StateGraph(State)

    workflow.add_node("invoke_proposer_agent", invoke_proposer_agent)
    workflow.add_node("get_input_humano", get_input_humano)
    workflow.add_node("invoke_buscador_de_padre_agent", invoke_buscador_de_padre_agent)
    workflow.add_node("buscar_nodo_padre", invoke_buscador_de_padre_agent)
    workflow.add_node("anadir_nodo_al_arbol", anadir_nodo_al_arbol)


    workflow.add_edge(START, "invoke_proposer_agent")
    workflow.add_edge("invoke_proposer_agent", "get_input_humano")
    workflow.add_conditional_edges("get_input_humano", conditional_anadir_tecnologia_al_arbol)
    workflow.add_edge("buscar_nodo_padre", "anadir_nodo_al_arbol")
    workflow.add_edge("anadir_nodo_al_arbol", END)

    initial_state = State(
        herramienta_necesaria=herramienta_necesaria,
        tecnologias_rechazadas=tecnologias_rechazadas,
        tecnologia_propuesta="",
        anadir_tecnologia_al_arbol=None,
        nodo_padre_id=None,
        nodo_anadido=None
    )

    memory = MemorySaver()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {
        "thread_id": thread_id
    }}

    graph = workflow.compile(checkpointer=memory, interrupt_before=["get_input_humano"])

    graph.invoke(initial_state, config=config)

    tecnologia_propuesta = graph.get_state(config).values["tecnologia_propuesta"]
    print("Se ha propuesto la tecnología: ", tecnologia_propuesta)
    anadir_tecnologia_al_arbol_str = input("¿Desea añadir la tecnología al árbol? (s/n): ")
    anadir_tecnologia_al_arbol = (anadir_tecnologia_al_arbol_str == "s"
                                  or anadir_tecnologia_al_arbol_str == "S"
                                  or anadir_tecnologia_al_arbol_str == "si"
                                  or anadir_tecnologia_al_arbol_str == "Si"
                                  or anadir_tecnologia_al_arbol_str == "SI")
    graph.update_state(config=config, values={"anadir_tecnologia_al_arbol": anadir_tecnologia_al_arbol})

    resultado = graph.invoke(None, config=config)

    if resultado is not None and resultado.get("nodo_anadido") is not None:
        nodo_anadido = resultado["nodo_anadido"]
        return nodo_anadido
    else:
        return None

