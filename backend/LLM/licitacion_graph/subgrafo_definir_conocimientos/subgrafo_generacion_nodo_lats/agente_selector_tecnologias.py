import copy

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from LLM.licitacion_graph.DatosLicitacion import DatosLicitacion
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.clases_para_lats import \
    PropuestaProyecto
from LLM.llm_utils import LLM_utils
from LLM.llm_utils.RetryGraph_decorator import bind_validator_with_retries
from LLM.llm_utils.add_modify_messages_to_chatprompttemplate_decorator import get_modified_messages_chat_prompt_template

# Ponerle tempreatura alta para que no salgan siempre las mismas opciones a la hora de generar las opciones en el árbol LATS
llm = LLM_utils.get_model(temperatura=1)

system = """
Eres un agente especializado en seleccionar las tecnologías más adecuadas para un proyecto software de tipo {categoria_proyecto}. 
El proyecto software deriva de una licitación, por lo que ten encuenta los requisitos de la licitación, también pueden haber requisitos adicionales.
Se te proporcionará una lista de etapas, junto con una lista de herramientas necesarias, a su vez, cada herramienta necesaria tiene una lista de tecnologías posibles.
Debes seleccionar únicamente una tecnología por cada herramienta necesaria.
ATENCION: La tecnología seleccionada debe ser parte de la lista proporcionada. Si se selecciona otra tecnología, un sistema crítico fallará. Incluso si en la reflexión
se mencionan otras tecnologías, sólo puedes seleccionar una de la lista proporcionada.


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
            """)
    ]
)


def invoke_seleccionar_tecnologias(datos_licitacion: DatosLicitacion, mensajes_feedback: list[BaseMessage], mensajes_modificacion: list[BaseMessage]):
    # copiarlo deep para crear uno nuevo en cada invocación
    current_prompt = copy.deepcopy(agent_selector_prompt)

    licitacion = datos_licitacion.licitacion
    requisitos_adicionales = datos_licitacion.requisitos_adicionales
    categoria_proyecto = datos_licitacion.categoria_proyecto
    requisitos_etapas = datos_licitacion.get_requisitos_etapas_str()

    prompt_dict = {
        "licitacion": licitacion,
        "requisitos_adicionales": requisitos_adicionales,
        "categoria_proyecto": categoria_proyecto,
        "etapas_proyecto": requisitos_etapas,
        "mensajes_modificacion": mensajes_modificacion
    }

    current_prompt = get_modified_messages_chat_prompt_template(current_prompt, mensajes_modificacion)

    # En caso de que el feedback esté vacío (cuando se crea el nodo raíz) no añadir el placeholder
    if mensajes_feedback:
        current_prompt.messages.append(MessagesPlaceholder(variable_name="mensajes_feedback"))
        prompt_dict["mensajes_feedback"] = mensajes_feedback

    current_agent = current_prompt | bind_validator_with_retries(
        llm=llm.with_config(run_name="AgentSelector"),
        tools=[PropuestaProyecto],
        tool_choice="any"
    )

    proyecto = current_agent.invoke(prompt_dict)
    return proyecto
