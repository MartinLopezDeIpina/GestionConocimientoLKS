import operator
from typing import TypedDict, Annotated
from langgraph.constants import START, END, Send
from langgraph.graph import StateGraph


class StateHerramienta(TypedDict):
    herramienta_necesaria: str
    result: str


class State(TypedDict):
    herramientas_necesarias: list[str]
    resultados_herramientas: Annotated[list[str], operator.add]


def invoke_herramientas(state: State):
    herramientas = state["herramientas_necesarias"]

    return [Send("ejecutar_herramienta",
                 {
                        "herramienta_necesaria": herramienta,
                 }) for herramienta in herramientas]


def ejecutar_herramienta(state: StateHerramienta):
    herramienta_necesaria = state["herramienta_necesaria"]

    result = f"ejecutando herramienta {herramienta_necesaria}"

    return {"resultados_herramientas": [result]}


def printear_resultados_herramientas(state: State):
    for result in state["resultados_herramientas"]:
        print(result)


def invoke_subgrafo_prueba_herramientas(herramientas_necesarias: list[str]):
    workflow = StateGraph(State)

    workflow.add_node("ejecutar_herramienta", ejecutar_herramienta)
    workflow.add_node("printear_resultados_herramientas", printear_resultados_herramientas)

    workflow.add_conditional_edges(START, invoke_herramientas, ["ejecutar_herramienta"])
    workflow.add_edge("ejecutar_herramienta", "printear_resultados_herramientas")
    workflow.add_edge("printear_resultados_herramientas", END)

    initial_state = State(
        herramientas_necesarias=herramientas_necesarias,
        resultados_herramientas=[]
    )

    graph = workflow.compile()
    result = graph.invoke(initial_state)
    return result["resultados_herramientas"]



