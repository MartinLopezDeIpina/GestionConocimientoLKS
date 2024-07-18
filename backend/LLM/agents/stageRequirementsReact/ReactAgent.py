from langchain_core.agents import AgentAction
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from LLM.LLM_utils import get_model, get_tool_name

model = get_model()


system_prompt = PromptTemplate.from_template("""
Eres un experto en la captura de requisitos para proyectos de software de {categoria_proyecto}.
Debes realizar la captura de requisitos para la etapa '{etapa_proyecto}' de un proyecto de software extraído de una licitación.
La licitación es la siguiente: \n\n{licitacion}\n
Se han identificado las siguintes etapas del proyecto: \n\n{etapas_proyecto}\n
Tú debes encargarte de la captura de requisitos de la etapa '{etapa_proyecto}'.

Debes seguir los siguintes pasos: 
1. Realizar una captura de requisitos inicial.
2. Buscar con la herramienta de búsqueda requisitos que puedan ser relevantes para la etapa del proyecto.
3. Modificar la captura de requisitos actual con los nuevos requisitos encontrados, puedes eliminar, modificar o agregar nuevos requisitos. 
4. Si se considera que no hay que modificar más requisitos, finaliza la captura de requisitos llamando al tool RequisitosFinal.

Usa el siguiente formato: 
Pensamiento: Siempre debes pensar antes de actuar
Accion: Ejecutar una de las siguientes tools: {tools} Es crucial que SOLO llames UNA tool en cada acción
Observacion: el resultado de la acción tras haberla ejecutado
... (Este ciclo Pensamiento-Accion-Observación se repite hasta que el pensamiento decida que no hay más requisitos que agregar, ejecutando así la acción final)

En caso de que la captura de requisitos ya haya comenzado, continúa con el siguiente paso:

Estado de la captura de requisitos:
{agent_scratchpad}
""")


def create_scratchpad(intermediate_steps: list[AgentAction]):
    steps = []
    for i, action in enumerate(intermediate_steps):
        if action.log != "TBD":
            steps.append(
                f"Tool: {action.tool}, input: {action.tool_input}\n"
                f"Output: {action.log}"
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
    )
    # tool_choice le obliga al LLM a elegir una tool en cada paso
    model_react = model.bind_tools(tools, tool_choice="any")
    chain = variables | prompt | model_react

    return chain


