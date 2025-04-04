from langchain_core.agents import AgentAction
from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate, FewShotChatMessagePromptTemplate, \
    ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from LLM.llm_utils.LLM_utils import get_model, get_tool_name
from LLM.llm_utils.RetryGraph_decorator import bind_validator_with_retries
from LLM.llm_utils.add_modify_messages_to_chatprompttemplate_decorator import get_modified_messages_chat_prompt_template

model = get_model()

system_prompt = """
Eres un experto en la captura de requisitos tecnológicos (herramientas) para proyectos de software de {categoria_proyecto}.
Debes determinar qué tipo de herramientas serán necesarias para la etapa '{etapa_proyecto}' de un proyecto de software extraído de una licitación.
El tipo de herramienta será lo más concreto posible, sin especificar la implementación de la tecnología. Por ejemplo, 'Arquitectura de microservicios' es demasiado genral, ya que no podría ser instanciado por ninguna implementación. En su lugar, podrías decir 'Herramienta de orquestación de componentes de microservicios'. Por otro lado, 'Docker' o 'Spring Boot' son ejemplos de herramientas concretas, no de tipos de herramientas.

Debes seguir los siguintes pasos: 
1. Generar una lista de herramientas iniciales. 
2. Buscar con la tool de búsqueda requisitos tecnológicos que puedan ser relevantes para la etapa del proyecto. En caso de encontrar implementaciones de tecnologías, debes considerar los tipos de tecnologías, no las implementaciones. Por ejemplo, si se encuentras necesaria una tecnología como 'CSS', considera 'Herramienta de estilado'.
3. Modificar la captura actual con las nuevas herramientas encontradas, puedes eliminar, modificar o agregar nuevas tecnologías. 
4. Si se considera que no hay que modificar más herramientas, finaliza la captura llamando al tool RequisitosFinal.

Usa el siguiente formato: 
Pensamiento: Siempre debes razonar antes de actuar. 
Accion: Ejecutar SOLAMENTE UNA de las siguientes tools: {tools}  (La tool inicial SOLO se ejecutará en el primer paso, si la captura ya contiene pasos, NO la llames). ATENCION SI NO SE CUMPLE EL FORMATO DE LA TOOL, O SE LLAMA A MÁS DE UNA TOOL, UN SISTEMA CRITICO FALLARA. 
Observacion: el resultado de la acción tras haberla ejecutado
... (Este ciclo Pensamiento-Accion-Observación se repite hasta que el pensamiento decida que no hay más requisitos que agregar, ejecutando así la acción final)

Es muy importante que la cantidad de herramientas iniciales sean AL MENOS 2 y MAXIMO 5. SI SE MANDAN MAS DE 5, UN SISTEMA CRITICO FALLARA.

En caso de que la captura de requisitos tecnológicos ya haya comenzado, continúa con el siguiente paso:
"""

ejemplos = [
    {
        "etapa": "Diseño",
        "categoria": "Desarrollo de aplicación web",
        "tecnologias": ["Herramienta de diseño de UI/UX", "Herramienta de prototipado", "Herramienta de wireframing"]
    },
    {
        "etapa": "Implementación backend",
        "categoria": "Desarrollo de aplicación web",
        "tecnologias": ["Lenguaje de programación backend", "Framework de backend", "Herramienta de base de datos", ]
    },
    {
        "etapa": "Aseguramiento de calidad",
        "categoria": "Desarrollo de aplicación web",
        "tecnologias": ["Herramienta de pruebas automatizadas", "Herramienta de gestión de incidencias",
                        "Herramienta de análisis estático de código"]
    }
]

user_prompt = """
La licitación es la siguiente: \n\n{licitacion}\n
También se tienen los siguientes requisitos adicionales: \n\n{requisitos_adicionales}\n
Se han identificado las siguintes etapas del proyecto: \n\n{etapas_proyecto}\n
Tú debes encargarte únicamente de la etapa '{etapa_proyecto}'.
"""

plantilla_ejemplo = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(
        "Ejemplo etapa {etapa} en '{categoria}':\n{tecnologias}"
    )
])

few_shot_chat_prompt_template = FewShotChatMessagePromptTemplate(
    example_prompt=plantilla_ejemplo,
    examples=ejemplos,
    # Dejarlo vacío porquqe son variables solo para los ejemplos
    input_variables=[]
)


def create_scratchpad(intermediate_steps: list[AgentAction]):
    steps = []
    for i, action in enumerate(intermediate_steps):
        if action.log != "TBD":
            if "observacion" not in action.tool_input:
                print("problemas_debug")
            steps.append(
                AIMessage(content=
                          f"Pensamiento: {action.tool_input['pensamiento']}\n" +
                          f"Accion: {action.tool}\n"
                          f"Observacion: {action.tool_input['observacion']}"
                          )
            )
    return steps


def get_tools_names(tools):
    tool_names = []
    for tool_obj in tools:
        tool_names.append(get_tool_name(tool_obj))
    return ", ".join(tool_names)


def get_react_agent(tools, mensajes_modificacion):
    tools_names = get_tools_names(tools)

    variables = {
        "agent_scratchpad": lambda x: create_scratchpad(
            intermediate_steps=x["intermediate_steps"]
        ),
        "licitacion": lambda x: x["datos_licitacion"].licitacion,
        "requisitos_adicionales": lambda x: x["datos_licitacion"].requisitos_adicionales,
        "etapas_proyecto": lambda x: x["datos_licitacion"].etapas_proyecto,
        "etapa_proyecto": lambda x: x["etapa_proyecto"],
        "categoria_proyecto": lambda x: x["datos_licitacion"].categoria_proyecto,
        "mensajes_modificacion": lambda x: x["mensajes_modificacion"],
    }

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            few_shot_chat_prompt_template,
            ("human", user_prompt),
        ]
    )
    complete_prompt = get_modified_messages_chat_prompt_template(prompt, mensajes_modificacion)

    complete_prompt.append(MessagesPlaceholder(variable_name="agent_scratchpad"))

    complete_prompt = complete_prompt.partial(
        tools=tools_names,
    )
    # tool_choice le obliga al LLM a elegir una tool en cada paso
    model_react = bind_validator_with_retries(llm=model, tools=tools, tool_choice="any")
    chain = variables | complete_prompt | model_react

    return chain
