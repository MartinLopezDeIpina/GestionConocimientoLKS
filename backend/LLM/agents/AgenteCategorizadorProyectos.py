from langchain.globals import set_debug
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI


class Categoria(BaseModel):
    categoria_proyecto: str = Field(description="categoría del proyecto software")


model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, verbose=True)
set_debug(True)

prompt_template = PromptTemplate.from_template(
"""
Eres un agente especializado en la categorización de proyectos software. 
Dada una licitación y una lista de requisitos adicionales, debes determinar la categría del proyecto.
Debes incluir únicamente la categoría general del proyecto, independientemente del dominio de la licitación.
Algunos ejemplos de categorías podrían ser las siguientes, aunque no se limitan a ellas: 
- Desarrollo de aplicación web
- Desarrollo de aplicación móvil
- Consultoría en ciberseguridad
- Consultoría de software

Licitación: {licitacion}
Requisitos adicionales: {requisitos_adicionales}
"""
)


def get_proyect_definer_agetn_run_output(licitacion, requisitos_adicionales):
    requisitos_adicionales = "\n".join(requisitos_adicionales)

    chain = prompt_template | model.with_structured_output(Categoria)
    result = chain.invoke({"licitacion": licitacion, "requisitos_adicionales": requisitos_adicionales})
    return result.categoria_proyecto




