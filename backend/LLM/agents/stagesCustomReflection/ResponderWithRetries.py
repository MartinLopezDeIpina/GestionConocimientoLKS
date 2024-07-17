import json

from langchain_core.messages import ToolMessage
from langchain_core.pydantic_v1 import ValidationError
from langchain.globals import set_debug
from langchain_openai import ChatOpenAI

from LLM.agents.stagesCustomReflection.AnswerQuestion import AnswerQuestion
from LLM.agents.stagesCustomReflection.State import State

model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, verbose=True)
set_debug(True)


class ResponderWithRetries:
    def __init__(self, runnable, validator):
        self.runnable = runnable
        self.validator = validator

    def respond(self, state: State):
        for attempt in range(3):
            response = self.runnable.invoke(
                {}
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
                validation_error = f"{repr(e)}\n\nPresta atención al esquema requerido.\n\n" + self.validator.schema_json() + "Responde corrigiendo los errores de validación."
                return {"validation_error": validation_error}

        return {"critica_actual": None}