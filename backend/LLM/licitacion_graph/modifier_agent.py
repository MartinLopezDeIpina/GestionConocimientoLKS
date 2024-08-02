from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import enum

from LLM.licitacion_graph.DatosLicitacion import DatosLicitacion
from LLM.llm_utils import LLM_utils


class Subgrafo(enum.Enum):
    INICIAL = "proyect_definer_model"
    DEFINIR_HERRAMIENTAS_DE_ETAPAS = "proyect_tools_subgraph"
    DEFINIR_CONOCIMIENTOS = "lats_subgrafo_definir_conocimientos"


class Modificacion(BaseModel):
    """Cuál modificación realizar a la propuesta de proyecto"""
    sugrafo_a_llamar: Subgrafo = Field(description="Subgrafo a llamar")
    index_etapas_a_modificar: list[int] = Field(description="Índices de las etapas a modificar. Empezando por 0. Si no se modifica ninguna etapa, dejar vacío.")


llm = LLM_utils.get_model()
structured_llm_modifier = llm.with_structured_output(Modificacion)

system = """
Eres un agente especializado en determinar qué modificaciones realizar a una propuesta de un proyecto software.
Se te proporcionará una propuesta de proyecto software definida desde una licitación.
Se te proporcionará también un feedback de un experto en la propuesta de proyecto software.
Debes determinar qué modificaciones realizar basándote en el feedback recibido.
La propuesta de proyecto software está dividida en etapas. Cada etapa tiene una serie de herramientas que es una forma abstracta de representar el tipo de conocimientos que podrían representar estas herramientas. Por ejemplo, en la etapa de 'Desarrollo frontend', 'Framework Frontend' es una herramienta y 'React' es el conocimiento que representa esta herramienta.

Tienes 3 posibles opciones: 
- INICIAL(proyect_definer_model): empezar la propuesta de nuevo. Elegirla en caso de que el feedback requiera reestructurar las etapas del proyecto. Por ejemplo, si el feedback dice algo como "Fusionar las dos primeras etapas"
- DEFINIR_HERRAMIENTAS_DE_ETAPAS(proyect_tools_subgraph): modificar las herramientas de las etapas del proyecto. Elegirla en caso de que el feedback requiera cambiar el tipo de herramientas de las etapas del proyecto. Por ejemplo, si el feedback dice algo como "No utilizar un framework backend en la etapa X".
- DEFINIR_CONOCIMIENTOS(lats_subgrafo_definir_conocimientos): modificar los conocimientos de las etapas del proyecto. Elegirla en caso de que el feedback requiera cambiar el tipo de conocimientos de las etapas del proyecto. Por ejemplo, si el feedback dice algo como "".

En caso de elegir DEFINIR_HERRAMIENTAS_DE_ETAPAS o DEFINIR_CONOCIMIENTOS, se te pedirá que indiques los índices de las etapas a modificar, dejando las demás sin modificaciones. Por ejemplo, si se te pide que cambies el conocimiento de React por Angular, deberás indicar la etapa en la que se encuentra React.
"""

ejemplos = [
    {
        "feedback": "Usar React en vez de Angular",
        "modificacion_seleccionada": "lats_subgrafo_definir_conocimientos"
    },
    {
        "feedback": "No usar framework frontend, hacerlo desde el propio backend",
        "modificacion_seleccionada": "proyect_tools_subgraph"
    },
    {
        "feedback": "Quitar etapa de calidad",
        "modificacion_seleccionada": "proyect_definer_model"
    },
]

plantilla_ejemplo = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(
        "Ejemplo feedback: {feedback}\nRespuesta: {modificacion_seleccionada}"

    )
])

few_shot_chat_prompt_template = FewShotChatMessagePromptTemplate(
    example_prompt=plantilla_ejemplo,
    examples=ejemplos,
    # Dejarlo vacío porquqe son variables solo para los ejemplos
    input_variables=[]
)

modifier_agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        few_shot_chat_prompt_template,
        ("human", "Propuesta de proyecto: \n\n {propuesta} \n\nFeedback: {feedback}"),
    ]
)

modifier_agent = modifier_agent_prompt | structured_llm_modifier


def invoke_modificar_propuesta(datos_licitacion: DatosLicitacion, feedback: str):
    propuesta = datos_licitacion.get_requisitos_etapas_str()

    modificacion = modifier_agent.invoke({"propuesta": propuesta, "feedback": feedback})

    return modificacion
