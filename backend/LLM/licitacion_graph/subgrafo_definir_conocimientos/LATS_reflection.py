from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers.openai_tools import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import chain as as_runnable

from LLM.llm_utils import LLM_utils

llm = LLM_utils.get_model()


class Reflection(BaseModel):
    reflections: str = Field(
        description="La crítica constructiva sobre la propuesta del candidato."
    )
    score: int = Field(
        description="Nota de la propuesta. Debe estar entre 0 y 10.",
        gte=0,
        lte=10,
    )
    found_solution: bool = Field(
        description="Si la propuesta del candidato cumple con todos los requisitos en la métrica."
    )

    def as_message(self):
        return HumanMessage(
            content=f"Reflexión: {self.reflections}\nPuntuación: {self.score}"
        )

    @property
    def normalized_score(self) -> float:
        return self.score / 10.0


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Eres un agente especializado en puntuar la calidad de una propuesta de proyecto software en base a una licitación.
            Se te va a presentar una licitación con varios requisitos adicionales, junto con una propuesta de proyecto software.
            Reflexiona y puntúa la calidad de la respuesta del candidato.
            Utiliza la siguiente métrica para puntuar la calidad de la respuesta:
            - 0-3: La propuesta no contiene tecnologías suficientes para cumplir con los requisitos de la licitación.
            - 4-5: La propuesta contiene tecnologías suficientes para cumplir con los requisitos de la licitación, pero no cumple con todos los requisitos adicionales.
            - 6-7: La propuesta contiene tecnologías suficientes para cumplir con los requisitos de la licitación y cumple con todos los requisitos adicionales, pero las tecnologías son incompatibles entre sí.
            - 8-10: La propuesta contiene tecnologías suficientes para cumplir con los requisitos de la licitación, cumple con todos los requisitos adicionales y las tecnologías son compatibles entre sí.
            
            Finalmente, indica en la reflexión cuáles han sido los motivos de la nota proporcionada y cómo se podría mejorar la propuesta.
            """
        ),
        ("human", """
        Licitación: {licitacion}
        Requisitos adicionales: {requisitos_adicionales}
        """),
        MessagesPlaceholder(variable_name="candidato"),
    ]
)

reflection_llm_chain = (
    prompt
    | llm.bind_tools(tools=[Reflection], tool_choice="Reflection").with_config(
        run_name="Reflection"
    )
    | PydanticToolsParser(tools=[Reflection])
)


@as_runnable
def reflection_chain(inputs) -> Reflection:
    licitacion = inputs["licitacion"]
    requisitos_adicionales = inputs["requisitos_adicionales"]
    candidato = inputs["candidato"]

    tool_choices = reflection_llm_chain.invoke({
        "licitacion": licitacion,
        "requisitos_adicionales": requisitos_adicionales,
        "candidato": candidato,
    })
    reflection = tool_choices[0]
    if not isinstance(inputs["candidato"][-1], AIMessage):
        reflection.found_solution = False
    return reflection
