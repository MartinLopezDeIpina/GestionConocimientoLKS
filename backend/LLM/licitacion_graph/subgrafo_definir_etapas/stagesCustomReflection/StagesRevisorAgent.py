from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.pydantic_v1 import Field

from LLM.licitacion_graph.subgrafo_definir_etapas.stagesCustomReflection.ResponderWithRetries import ResponderWithRetries
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesCustomReflection.StagesResponderAgent import model, actor_prompt_template
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesCustomReflection.AnswerQuestion import AnswerQuestion
from langchain_core.prompts import PromptTemplate


revise_instructions = PromptTemplate.from_template(
    """
Debes generar una crítica para mejorar la siguiente propuesta de etapas para el proyecto: {propuesta_etapas}
    - Sé severo para maximizar la mejora.
    - Sé específico a la hora de criticar, 1 frase por propuesta de cambio. Evita ambigüedades como 'no abarca todo lo mencionado en la licitación' o 'se deberían combinar algunas etapas'. En su lugar, proporciona detalles específicos sobre qué etapas deberían ser modificadas y por qué.
    - Recomienda consultas de búsqueda para investigar información sobre los elementos a mejorary mejorar tu respuesta.
    - Ten en cuenta el máximo  (5) y mínimo (3) de etapas. Si hay demasiadas etapas, prioriza recomendar fusionar etapas. Si hay muy pocas, prioriza recomendar dividir etapas.
    
Debes utilizar la siguiente función para generar tu respuesta: EtapasProyecto
{validacion_error}
    """
)


class ReviseAnswer(AnswerQuestion):
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

