from langchain_core.output_parsers import PydanticToolsParser, PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from pydantic.v1 import conlist

from LLM.equipo_graph.DatosEquipo import DatosEquipo
from LLM.licitacion_graph.DatosLicitacion import DatosLicitacion
from LLM.llm_utils import LLM_utils
from LLM.llm_utils.RetryGraph_decorator import bind_validator_with_retries
from database import db
from models import NodoArbol


class ComposicionPuestos(BaseModel):
    """Tipos de puestos de trabajo junto la cantidad de personas que ocupan cada puesto"""
    puestos: dict[str, int] = Field(
        ..., description="Tipos de puestos de trabajo junto la cantidad de personas que ocupan cada puesto"
    )

llm = LLM_utils.get_model()

system = """
Eres un agente especializado en definir puestos de trabajo dado un proyecto software y la cantidad de trabajadores.
Debes definir los puestos de trabajo y la cantidad de personas que ocupan cada puesto.
En caso de que haya muchos puestos de trabajo, los puestos deben ser más concretors, mientras que si hay pocos puesto de trabajo, estos deben ser más generales.
{format_instructions}
"""

ejemplos = [
    {
        "categoria_proyecto": "Desarrollo de aplicación web",
        "cantidad_trabajadores": 2,
        "respuesta": {
            "puestos": {
            "Desarrollador Fullstack": 1,
            "Especialista en Infraestructura": 1
            }
        }
    },
    {
        "categoria_proyecto": "Desarrollo de aplicación web",
        "cantidad_trabajadores": 10,
        "respuesta": {
            "puestos": {
            "Gestor de Proyecto": 1,
            "Diseñador UX/UI": 1,
            "Desarrollador Frontend": 2,
            "Desarrollador Backend": 2,
            "Especialista en Seguridad": 1,
            "Especialista en Bases de Datos": 1,
            "Especialista en Infraestructura": 1,
            "Especialista en Testing": 1
            }
        }
    }
]

plantilla_ejemplo = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(
        "Ejemplo para {categoria_proyecto} con {cantidad_trabajadores} trabajadores:\n{respuesta}"
    )
])

few_shot_chat_prompt_template = FewShotChatMessagePromptTemplate(
    example_prompt=plantilla_ejemplo,
    examples=ejemplos,
    # Dejarlo vacío porquqe son variables solo para los ejemplos
    input_variables=[]
)


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        few_shot_chat_prompt_template,
        ("human", "Proyecto software:\nProyecto {categoria_proyecto}\nCantidad de trabajadores: {cantidad_trabajadores}\nDescripción del proyecto: {descripcion_proyecto}\n"),
    ]
)

validator = PydanticOutputParser(pydantic_object=ComposicionPuestos)
partial_variables = {
    "format_instructions": validator.get_format_instructions()
}
prompt = prompt.partial(**partial_variables)

agent = prompt | llm | validator


def invoke_composicion_de_puestos(datos_licitacion: DatosLicitacion, datos_equipo: DatosEquipo):
    cantidad_trabajadores = datos_equipo.cantidad_trabajadores
    categoria_proyecto = datos_licitacion.categoria_proyecto
    descripcion_proyecto = datos_licitacion.get_requisitos_etapas_str()

    result = agent.invoke({
        "cantidad_trabajadores": cantidad_trabajadores,
        "categoria_proyecto": categoria_proyecto,
        "descripcion_proyecto": descripcion_proyecto
    })

    return result.puestos

