import operator
from typing import Annotated, Any

import asyncio

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

from LLM.agents.AgenteCategorizadorProyectos import get_proyect_definer_agetn_run_output


class State(TypedDict):
    licitacion: str
    requisitos_adicionales: list[str]

    categoria_proyecto: str


def invoke_proyect_definer_model(state: State):
    licitacion = state["licitacion"]
    requisitos_adicionales = state["requisitos_adicionales"]

    resultado = get_proyect_definer_agetn_run_output(licitacion, requisitos_adicionales)
    return {"categoria_proyecto": resultado}


def nodo_vacio(state: State):
    return state


async def start_licitacion_graph(licitacion, requisitos_adicionales):
    workflow = StateGraph(State)

    workflow.add_node("proyect_definer_model", invoke_proyect_definer_model)
    workflow.add_node("nodo_vacio", nodo_vacio)

    workflow.add_edge(START, "proyect_definer_model")
    workflow.add_edge("proyect_definer_model", "nodo_vacio")
    workflow.add_edge("nodo_vacio", END)

    initial_state = State(licitacion=licitacion, requisitos_adicionales=requisitos_adicionales, categoria_proyecto="")

    graph = workflow.compile()

    async for output in graph.astream(initial_state, stream_mode="values"):
        print(output)


licitacion_ejemplo = """
Licitación para el Desarrollo de una Aplicación Web de Reserva de Tickets de Cine

Referencia de Licitación: LIC-2024-001
1. Introducción

Cinemas XYZ invita a empresas desarrolladoras de software a presentar propuestas para el desarrollo de una aplicación web destinada a la reserva de tickets de cine. El presupuesto asignado para este proyecto es de $100,000 USD.
2. Objetivo del Proyecto

Desarrollar una aplicación web intuitiva y fácil de usar que permita a los usuarios:

    Buscar y seleccionar películas.
    Elegir horarios y asientos disponibles.
    Realizar el pago de los tickets de forma segura.
    Recibir confirmación y ticket electrónico por correo.

3. Alcance del Proyecto

La aplicación deberá incluir, pero no se limitará a, las siguientes características:

    Interfaz de Usuario (UI)
        Diseño atractivo y responsivo.
        Navegación fácil y fluida.
        Motor de búsqueda para películas y horarios.
        Selección de asientos interactiva.

    Funcionalidades
        Registro y autenticación de usuarios.
        Búsqueda y filtrado de películas por género, fecha y horario.
        Visualización de asientos disponibles en tiempo real.
        Integración con pasarelas de pago seguras.
        Envío de confirmaciones y tickets electrónicos a través de correo electrónico.

    Backend
        Gestión de películas, horarios y disponibilidad de asientos.
        Base de datos robusta y segura para almacenar información de usuarios y transacciones.
        API para la integración con sistemas externos si es necesario (por ejemplo, sistemas de cine existentes).

    Administración
        Panel de administración para la gestión de películas, horarios y ventas.
        Reportes y análisis de ventas.
        Gestión de usuarios y roles administrativos.

4. Requisitos Técnicos

    Compatibilidad: La aplicación debe ser multiplataforma y funcionar correctamente en navegadores web modernos.
    Seguridad: Cumplimiento con las mejores prácticas de seguridad web y protección de datos.
    Integraciones: Debe incluirse la capacidad de integración con pasarelas de pago y otros sistemas relevantes.

5. Plazos y Entregables

    Duración del Proyecto: 6 meses desde la adjudicación del contrato.
    Entregables:
        Documento de especificaciones técnicas y de diseño (primer mes).
        Prototipo funcional (tercer mes).
        Versión beta para pruebas internas (quinto mes).
        Versión final de la aplicación y lanzamiento (sexto mes).
        Documentación completa y capacitación para el equipo de administración.

6. Presupuesto

El presupuesto máximo asignado para este proyecto es de $100,000 USD. Las propuestas deben incluir una descomposición detallada de costos, incluyendo:

    Costos de desarrollo.
    Diseño de la interfaz de usuario.
    Pruebas y aseguramiento de la calidad.
    Documentación y capacitación.
    Mantenimiento y soporte inicial.

7. Proceso de Selección

Las propuestas serán evaluadas en base a los siguientes criterios:

    Experiencia y capacidad técnica del proveedor.
    Calidad del diseño propuesto y usabilidad de la interfaz.
    Enfoque y metodología de desarrollo.
    Detalle y realismo del cronograma propuesto.
    Relación costo-beneficio.

8. Presentación de Propuestas

Las empresas interesadas deben enviar sus propuestas antes del 15 de agosto de 2024 a la siguiente dirección de correo electrónico: licitaciones@cinemasxyz.com.

Las propuestas deben incluir:

    Descripción de la empresa y portafolio de proyectos similares.
    Plan de trabajo detallado.
    Cronograma de desarrollo.
    Presupuesto desglosado.
    Perfiles de los miembros clave del equipo de desarrollo.

9. Contacto

Para consultas adicionales, contactar a:

Nombre: Juan Pérez
Correo electrónico: juan.perez@cinemasxyz.com
Teléfono: +1 234 567 890

Esperamos recibir sus propuestas y trabajar juntos en este emocionante proyecto para mejorar la experiencia de nuestros clientes en Cinemas XYZ.

Cinemas XYZ
Fecha de Emisión: 15 de julio de 2024
"""

requisitos_adicionales_ejemplo = ["Utilizar un framework de javascript para el frontend", "La base de datos debe ser PostgreSQL"]


def test_start_licitacion_graph():
    asyncio.run(start_licitacion_graph(licitacion_ejemplo, requisitos_adicionales_ejemplo))

