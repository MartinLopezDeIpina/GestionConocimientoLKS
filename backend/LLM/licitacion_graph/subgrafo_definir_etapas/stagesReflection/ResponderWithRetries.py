import json

from langchain_core.messages import ToolMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import ValidationError
from langchain.globals import set_debug
from langchain_openai import ChatOpenAI

from LLM.licitacion_graph.subgrafo_definir_etapas.stagesReflection.AnswerQuestion import AnswerQuestion
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesReflection.State import State

model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, verbose=True)
set_debug(True)


actor_prompt_template = PromptTemplate.from_template(
    """
Eres un agente especializado en determinar las etapas de un proyecto software categorizado como {categoria_proyecto}.
Se debe generar una lista de etapas técnicas para el proyecto software a partir de una licitación y requisitos adicionales.
No serán necesarias etapas de gestión de proyectos como análisis de requisitos o de viabilidad, solo etapas técnicas.
La licitación es la siguiente: {licitacion}
Los requisitos adicionales son: {requisitos_adicionales}

Los pasos que debes seguir son los siguientes:

1. {first_instruction}
2. Reflexiona y critica tu respuesta de etapas. Sé severo para maximizar la mejora.
3. Recomienda consultas de búsqueda para investigar información y mejorar tu respuesta de etapas.

Para responder, utiliza la función {function_name}.

Debes pensar paso por paso, piensa y razona cada decisión.
    """
)


class ResponderWithRetries:
    def __init__(self, runnable, validator):
        self.runnable = runnable
        self.validator = validator

    def respond(self, state: State):
        response = []
        for attempt in range(3):
            response = self.runnable.invoke(
                {"tags": [f"attempt:{attempt}"], "critica_actual": state["critica_actual"], "resultados_busqueda": state["resultados_busqueda"]}
            )
            try:
                self.validator.invoke(response)

                #Sacar el objeto AnswerQuestion de la respuesta del LLM, está en el primer tool_call
                additional_kwargs = response.additional_kwargs if hasattr(response, 'additional_kwargs') else {}
                tool_calls = additional_kwargs.get('tool_calls', [])
                if not tool_calls:
                    return None  # or handle error
                arguments_json = tool_calls[0].get('function', {}).get('arguments', '{}')
                arguments_dict = json.loads(arguments_json)
                critica_actual = AnswerQuestion(**arguments_dict)

                return {"critica_actual": critica_actual}
            except ValidationError as e:
                state = state + [
                    response,
                    ToolMessage(
                        content=f"{repr(e)}\n\nPay close attention to the function schema.\n\n"
                                + self.validator.schema_json()
                                + " Respond by fixing all validation errors.",
                        tool_call_id=response.tool_calls[0]["id"],
                    ),
                ]
        return {"critica_actual": response}
