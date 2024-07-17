from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.pydantic_v1 import Field

from LLM.agents.stagesCustomReflection.ResponderWithRetries import ResponderWithRetries
from LLM.agents.stagesCustomReflection.StagesResponderAgent import model, actor_prompt_template
from LLM.agents.stagesCustomReflection.AnswerQuestion import AnswerQuestion
from langchain_core.prompts import PromptTemplate


revise_instructions = PromptTemplate.from_template(
    """
Debes generar una crítica para mejorar la siguiente propuesta de etapas para el proyecto: {propuesta_etapas}
    - Sé severo para maximizar la mejora.
    - Sé específico a la hora de criticar, 1 frase por propuesta de cambio. Evita ambigüedades como 'no abarca todo lo mencionado en la licitación' o 'se deberían combinar algunas etapas'. En su lugar, proporciona detalles específicos sobre qué etapas deberían ser modificadas y por qué.
    - Recomienda consultas de búsqueda para investigar información sobre los elementos a mejorary mejorar tu respuesta..
    
Debes utilizar la siguiente función para generar tu respuesta: {function_name}
{validacion_error}
    """
)


# Extend the initial answer schema to include references.
# Forcing citation in the model encourages grounded responses
class ReviseAnswer(AnswerQuestion):
    """Revise your original answer to your question. Provide an answer, reflection,

    cite your reflection with references, and finally
    add search queries to improve the answer."""

    references: list[str] = Field(
        descripción="Citas que motivan tu respuesta actualizada."
    )


def get_revisor(licitacion, requisitos_adicionales, categoria_proyecto, propuesta_etapas, validacion_error):
    instructions = revise_instructions.format(
        propuesta_etapas=propuesta_etapas.etapas,
        function_name=ReviseAnswer.__name__,
        validacion_error=validacion_error
    )

    prompt_revisor = actor_prompt_template.partial(
        licitacion=licitacion,
        requisitos_adicionales="\n".join(requisitos_adicionales),
        categoria_proyecto=categoria_proyecto,
        instrucciones_agente=instructions,
    )
    model_revisor = model.bind_tools(tools=[ReviseAnswer])

    revision_chain = prompt_revisor | model_revisor
    revision_validator = PydanticToolsParser(tools=[ReviseAnswer])

    revisor = ResponderWithRetries(runnable=revision_chain, validator=revision_validator)
    return revisor

