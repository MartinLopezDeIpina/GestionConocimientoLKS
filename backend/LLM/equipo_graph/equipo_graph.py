import uuid
from typing import TypedDict

import numpy as np
from langgraph.checkpoint import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from scipy.optimize import linear_sum_assignment

from LLM.equipo_graph.DatosEquipo import DatosEquipo
from LLM.equipo_graph.composicion_puestos_agent import invoke_composicion_de_puestos
from LLM.equipo_graph.tecnologias_por_puesto_agent import invoke_tecnologias_por_puesto
from LLM.licitacion_graph.DatosLicitacion import DatosLicitacion
from database import db
from models import Usuario, ConocimientoUsuario


class State(TypedDict):
    datos_licitacion: DatosLicitacion
    datos_equipo: DatosEquipo


def node_generar_puestos_de_trabajo(state: State):
    datos_licitacion = state["datos_licitacion"]
    datos_equipo = state["datos_equipo"]

    puestos_y_cantidad = invoke_composicion_de_puestos(datos_licitacion, datos_equipo)

    datos_equipo.composicion_puestos_de_trabajo = puestos_y_cantidad
    return {"datos_equipo": datos_equipo}


def get_cantidad_trabajadores_user_input():
    while True:
        try:
            cantidad_trabajadores = int(input("Ingrese la cantidad de trabajadores: "))

            if cantidad_trabajadores <= 0:
                print("Por favor, ingrese un número mayor o igual a cero.")
            elif cantidad_trabajadores > 20:
                print("Por favor, ingrese un número menor o igual a 20")
            else:
                break

        except ValueError:
            print("Por favor, ingrese un número entero válido.")

    return cantidad_trabajadores


def node_generar_tecnologias_por_puesto(state: State):
    datos_licitacion = state["datos_licitacion"]
    datos_equipo = state["datos_equipo"]

    tecnologias_por_puesto = invoke_tecnologias_por_puesto(datos_licitacion, datos_equipo)

    datos_equipo.tecnologias_por_puesto = tecnologias_por_puesto
    return {"datos_equipo": datos_equipo}


def node_elegir_trabajadores(state: State):
    datos_equipo = state["datos_equipo"]

    usuarios = db.session.query(Usuario).all()
    user_ids = [usuario.email for usuario in usuarios]
    job_ids = get_list_from_dict(datos_equipo.composicion_puestos_de_trabajo)

    users = get_usuarios_skills_dict()
    jobs = datos_equipo.tecnologias_por_puesto

    cost_matrix = np.zeros((len(users), len(job_ids)))

    for i, user_id in enumerate(user_ids):
        for j, job_id in enumerate(job_ids):
            # Calculate the number of matching skills
            matching_skills = len(set(jobs[job_id]) & set(users[user_id]))
            # Use negative because the algorithm minimizes cost, but we want to maximize matching skills
            cost_matrix[i][j] = -matching_skills

    # Apply the Hungarian algorithm
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    # Create the assignments and fulfilled skills dictionaries
    assignments = {}

    for r, c in zip(row_ind, col_ind):
        user_id = user_ids[r]
        job_id = job_ids[c]

        if job_id in assignments:
            assignments[job_id] = assignments[job_id] + [user_id]
        else:
            assignments[job_id] = [user_id]

    datos_equipo.composicion_trabajadores = assignments

    return {"datos_equipo": datos_equipo}


def get_usuarios_skills_dict():
    dict_conocimientos = {}
    conocimientos_usuarios = db.session.query(ConocimientoUsuario).all()

    for conocimiento_usuario in conocimientos_usuarios:
        dict_conocimientos[conocimiento_usuario.usuario_email] = dict_conocimientos.get(conocimiento_usuario.usuario_email, []) + [conocimiento_usuario.nodoID]

    return dict_conocimientos


# Dado el dict con clave puesto y valor num de trabajadores en el puesto,
# devuelve una lista con la clave repetida tantas veces como el valor
def get_list_from_dict(dict):
    result_list = []
    for key, value in dict.items():
        result_list.extend([key] * value)
    return result_list


def start_equipo_graph(datos_licitacion: DatosLicitacion):
    workflow = StateGraph(State)

    workflow.add_node("node_generar_puestos_de_trabajo", node_generar_puestos_de_trabajo)
    workflow.add_node("node_generar_tecnologias_por_puesto", node_generar_tecnologias_por_puesto)
    workflow.add_node("node_elegir_trabajadores", node_elegir_trabajadores)

    workflow.add_edge(START, "node_generar_puestos_de_trabajo")
    workflow.add_edge("node_generar_puestos_de_trabajo", "node_generar_tecnologias_por_puesto")
    workflow.add_edge("node_generar_tecnologias_por_puesto", "node_elegir_trabajadores")
    workflow.add_edge("node_elegir_trabajadores", END)

    cantidad_trabajadores = get_cantidad_trabajadores_user_input()

    initial_state = State(
        datos_licitacion=datos_licitacion,
        datos_equipo=DatosEquipo(cantidad_trabajadores=cantidad_trabajadores)
    )

    graph = workflow.compile()

    result = graph.invoke(initial_state)

    return result



