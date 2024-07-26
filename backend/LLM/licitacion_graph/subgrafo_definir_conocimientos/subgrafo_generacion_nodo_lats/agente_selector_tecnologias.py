from langchain_core.prompts import ChatPromptTemplate
from LLM.licitacion_graph.DatosLicitacion import DatosLicitacion
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.clases_para_lats import \
    PropuestaProyecto
from LLM.llm_utils import LLM_utils


llm = LLM_utils.get_model()
structured_llm_agente_selector = llm.with_structured_output(PropuestaProyecto)

system = """
Eres un agente especializado en seleccionar las tecnologías más adecuadas para un proyecto software de tipo {categoria_proyecto}. 
El proyecto software deriva de una licitación, por lo que ten encuenta los requisitos de la licitación, también pueden haber requisitos adicionales.
Se te proporcionará una lista de etapas, junto con una lista de herramientas necesarias, a su vez, cada herramienta necesaria tiene una lista de tecnologías posibles.
Debes seleccionar únicamente una tecnología por cada herramienta necesaria.

Utiliza el siguiente criterio con el siguiente orden de prioridad: 
1. Requisitos del proyecto.
2. Compatibilidad de la tecnología con el resto del proyecto. 
3. Popularidad de la tecnología en el mercado actual. Elige la tecnología más popular.\n
"""

agent_selector_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human",
         """
         La licitación: {licitacion}
         Requisitos adicionales: {requisitos_adicionales}
         Lista de etapas junto a las herramientas necesarias y sus tecnologías posibles: {etapas_proyecto}
            """),
    ]
)

agente_selector_tecnologias = agent_selector_prompt | structured_llm_agente_selector


def invoke_seleccionar_tecnologias(datos_licitacion: DatosLicitacion):
    licitacion = datos_licitacion.licitacion
    requisitos_adicionales = datos_licitacion.requisitos_adicionales
    categoria_proyecto = datos_licitacion.categoria_proyecto

    requisitos_etapas = datos_licitacion.get_requisitos_etapas_str()

    proyecto = agente_selector_tecnologias.invoke({
        "licitacion": licitacion,
        "requisitos_adicionales": requisitos_adicionales,
        "categoria_proyecto": categoria_proyecto,
        "etapas_proyecto": requisitos_etapas
    })

    return proyecto
