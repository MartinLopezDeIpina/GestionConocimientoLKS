from langchain_core.agents import AgentAction
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_core.tools import tool
from LLM.LLM_utils import get_model, get_tool_name
from LLM.agents.stageRequirementsReact.RetryGraph import bind_validator_with_retries

model = get_model()


system_prompt = PromptTemplate.from_template("""
Eres un experto en la captura de requisitos tecnológicos (herramientas) para proyectos de software de {categoria_proyecto}.
Debes determinar qué tipo de herramientas serán necesarias para la etapa '{etapa_proyecto}' de un proyecto de software extraído de una licitación.
El tipo de herramienta será lo más concreto posible, sin especificar la implementación de la tecnología. Por ejemplo, 'Arquitectura de microservicios' es demasiado genral, ya que no podría ser instanciado por ninguna implementación. En su lugar, podrías decir 'Herramienta de orquestación de componentes de microservicios'. Por otro lado, 'Docker' o 'Spring Boot' son ejemplos de herramientas concretas, no de tipos de herramientas.

La licitación es la siguiente: \n\n{licitacion}\n
Se han identificado las siguintes etapas del proyecto: \n\n{etapas_proyecto}\n
Tú debes encargarte únicamente de la etapa '{etapa_proyecto}'.

Debes seguir los siguintes pasos: 
1. Generar una lista de herramientas iniciales. 
2. Buscar con la tool de búsqueda requisitos tecnológicos que puedan ser relevantes para la etapa del proyecto. En caso de encontrar implementaciones de tecnologías, debes considerar los tipos de tecnologías, no las implementaciones. Por ejemplo, si se encuentras necesaria una tecnología como 'CSS', considera 'Herramienta de estilado'.
3. Modificar la captura actual con las nuevas herramientas encontradas, puedes eliminar, modificar o agregar nuevas tecnologías. 
4. Si se considera que no hay que modificar más herramientas, finaliza la captura llamando al tool RequisitosFinal.

Usa el siguiente formato: 
Pensamiento: Siempre debes razonar antes de actuar. 
Accion: Ejecutar solamente una de las siguientes tools: {tools}  (La tool RequisitosInicial sólo se ejecutará en el primer paso). ATENCION SI NO SE CUMPLE EL FORMATO DE LA TOOL, UN SISTEMA CRITICO FALLARA. 
Observacion: el resultado de la acción tras haberla ejecutado
... (Este ciclo Pensamiento-Accion-Observación se repite hasta que el pensamiento decida que no hay más requisitos que agregar, ejecutando así la acción final)

Es muy importante que la cantidad de herramientas iniciales sean AL MENOS 2 y MAXIMO 5. SI SE MANDAN MAS DE 5, UN SISTEMA CRITICO FALLARA.

Aquí tienes algunos ejemplos:
{ejemplos}

En caso de que la captura de requisitos tecnológicos ya haya comenzado, continúa con el siguiente paso:

Estado de la captura de requisitos tecnológicos:
{agent_scratchpad}
""")


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
        "tecnologias": ["Herramienta de pruebas automatizadas", "Herramienta de gestión de incidencias", "Herramienta de análisis estático de código"]
    }
]


plantilla_ejemplo = PromptTemplate.from_template("""
Ejemplo etapa {etapa} en '{categoria}':
{tecnologias}
""")

ejemplos = FewShotPromptTemplate(
    example_prompt=plantilla_ejemplo,
    examples=ejemplos,
    input_variables=["etapa", "categoria", "tecnologias"],
    suffix="..."
)


def create_scratchpad(intermediate_steps: list[AgentAction]):
    steps = []
    for i, action in enumerate(intermediate_steps):
        if action.log != "TBD":
            steps.append(
                f"Pensamiento: {action.tool_input['pensamiento']}\n"
                f"Accion: {action.tool}\n"
                f"Observacion: {action.tool_input['observacion']}"
            )
    return "\n---\n".join(steps)


def get_tools_names(tools):
    tool_names = []
    for tool_obj in tools:
        tool_names.append(get_tool_name(tool_obj))
    return ", ".join(tool_names)


def get_react_agent(tools):
    tools_names = get_tools_names(tools)

    variables = {
        "agent_scratchpad": lambda x: create_scratchpad(
            intermediate_steps=x["intermediate_steps"]
        ),
        "licitacion": lambda x: x["main_state"]["licitacion"],
        "etapas_proyecto": lambda x: x["main_state"]["etapas_proyecto"],
        "etapa_proyecto": lambda x: x["etapa_proyecto"],
        "categoria_proyecto": lambda x: x["main_state"]["categoria_proyecto"],
    }

    prompt = system_prompt.partial(
        tools=tools_names,
        ejemplos=ejemplos.format()
    )
    # tool_choice le obliga al LLM a elegir una tool en cada paso
    #model_react = model.bind_tools(tools, tool_choice="any")
    model_react = bind_validator_with_retries(llm=model, tools=tools, tool_choice="any")
    chain = variables | prompt | model_react

    return chain


