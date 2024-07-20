from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesReflection.AnswerQuestion import AnswerQuestion
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesReflection.ResponderWithRetries import ResponderWithRetries, model, actor_prompt_template


def get_first_responder(licitacion, requisitos_adicionales, categoria_proyecto):
    responder_prompt = actor_prompt_template.partial(
        licitacion=licitacion,
        requisitos_adicionales="\n".join(requisitos_adicionales),
        categoria_proyecto=categoria_proyecto,
        first_instruction="Genera una lista inicial de etapas técnicas para el proyecto software.",
        function_name=AnswerQuestion.__name__,
    )
    responder_model = model.bind_tools(tools=[AnswerQuestion])

    initial_answer_chain = responder_prompt | responder_model
    validator = PydanticToolsParser(tools=[AnswerQuestion])

    first_responder = ResponderWithRetries(
        runnable=initial_answer_chain, validator=validator
    )
    return first_responder
