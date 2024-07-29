from langchain.globals import set_debug
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

from LLM.llm_utils import LLM_utils


class Categoria(BaseModel):
    categoria_proyecto: str = Field(description="categoría del proyecto software")


model = LLM_utils.get_model()
structured_llm_categorizador = model.with_structured_output(Categoria)

system = """
Eres un agente especializado en la categorización de proyectos de software. Dada una licitación y una lista de requisitos adicionales, debes determinar la categoría del proyecto. El nivel descriptivo de la categoría debe ser lo más específico posible sin mencionar el dominio. Es decir, si la licitación requiere desarrollar una aplicación web para reservar asientos en un cine, 'desarrollo de aplicación web para cine' es demasiado específico, mientras que 'desarrollo de aplicación' es demasiado ambígüo, la categroría correcta sería 'Desarrollo de aplicación web'.
Algunos proyectos software pueden requerir el desarrollo de un sistema que no se limita a un tipo de aplicación, en cuyo caso, evita categorías específicas y opta por categorías más generales.
Algunos ejemplos de categorías podrían ser las siguientes, aunque no se limitan a ellas:

    Desarrollo de aplicación web: Proyectos enfocados en crear aplicaciones cuyo principal medio de acceso sea a través de navegadores web.
    Desarrollo de aplicación móvil: Proyectos enfocados en crear aplicaciones cuyo principal medio de acceso sea a través de dispositivos móviles.
    Sistemas de gestión y administración: Proyectos enfocados en la creación de software para administrar y optimizar operaciones internas y externas, tales como CRM, ERP, HRM, etc.
    Consultoría en ciberseguridad: Proyectos enfocados en la evaluación y mejora de la seguridad informática.
    Consultoría de software: Proyectos que incluyen análisis, asesoramiento y diseño de soluciones de software sin desarrollo extensivo de código.
    Integración de sistemas: Proyectos que buscan conectar y hacer interoperables diferentes sistemas de software.
    Desarrollo de software personalizado: Proyectos que implican la creación de soluciones de software a medida para necesidades específicas de una organización.

Utiliza esta información para categorizar correctamente el proyecto basado en la licitación y los requisitos adicionales proporcionados.
"""

modifier_agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Licitación: {licitacion}\n\nRequisitos adicionales: {requisitos_adicionales}"),

    ]
)

agente_categorizador = modifier_agent_prompt | structured_llm_categorizador


def get_proyect_definer_agetn_run_output(licitacion, requisitos_adicionales):
    requisitos_adicionales = "\n".join(requisitos_adicionales)

    result = agente_categorizador.invoke({"licitacion": licitacion, "requisitos_adicionales": requisitos_adicionales})
    return result.categoria_proyecto




