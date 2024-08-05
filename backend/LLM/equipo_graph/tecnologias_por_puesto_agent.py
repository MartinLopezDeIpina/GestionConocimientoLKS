from typing import Dict, List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

from LLM.equipo_graph.DatosEquipo import DatosEquipo
from LLM.licitacion_graph.DatosLicitacion import DatosLicitacion
from LLM.llm_utils import LLM_utils


class TecnologiasPuestos(BaseModel):
    """Cada puesto de trbajo junto con las tecnologías que debe manejar"""
    tecnologias_por_puesto: Dict[str, List[int]] = Field(description="Cada puesto de trbajo junto con las tecnologías que debe manejar")

llm = LLM_utils.get_model()

system = """
Eres un agente especializado en clasificar tecnologías de un proyecto software por puesto de trabajo.
Dada una propuesta de proyecto software en la que se mencionan las tecnologías/conocimientos que se deben usar en cada etapa del proyecto y los puestos de trabajo que se necesitan para dicho proyecto,
debes clasificar las tecnologías/conocimientos por puesto de trabajo.
Alguna tecnología puede ser usada por varios puestos de trabajo.
Todas las tecnologías deben ser clasificadas, si una tecnología no encaja en ningun puesto, clasificala donde mejor encaje.
{format_instructions}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Proyecto software:\n{propuesta_proyecto}\nPuestos de trabajo: {puestos_trabajo}"),
    ]
)

validator = PydanticOutputParser(pydantic_object=TecnologiasPuestos)
partial_variables = {
    "format_instructions": validator.get_format_instructions()
}
prompt = prompt.partial(**partial_variables)

agent = prompt | llm | validator


def invoke_tecnologias_por_puesto(datos_licitacion: DatosLicitacion, datos_equipo: DatosEquipo):
    propuesta_proyecto = datos_licitacion.get_requisitos_etapas_str()
    puestos_trabajo = datos_equipo.composicion_puestos_de_trabajo

    result = agent.invoke({
        "propuesta_proyecto": propuesta_proyecto,
        "puestos_trabajo": puestos_trabajo
    })

    return result.tecnologias_por_puesto

