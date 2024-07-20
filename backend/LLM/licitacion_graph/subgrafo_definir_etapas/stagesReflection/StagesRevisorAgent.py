from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.pydantic_v1 import Field
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesReflection.StagesResponderAgent import model, ResponderWithRetries
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesReflection.AnswerQuestion import AnswerQuestion
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesReflection.ResponderWithRetries import actor_prompt_template
from langchain_core.prompts import PromptTemplate


revise_instructions = PromptTemplate.from_template(
    """Dada la respuesta anterior y su correspondiente crítica, tu respuesta debe ser una modificación de las etapas de la respuesta anterior basándose en la crítica generada. En caso de haber críticas, tu respuesta no puede ser una copia de la respuesta anterior.
    La respuesta de las etapas con la crítica correspondiente es: {critica_actual}
    Los resultados de la búsqueda de información adicional son: {resultados_busqueda}
    Los pasos que debes seguir para corregir la respuesta son los siguientes:
    - Debes usar la crítica anterior para agregar o modificar información importante a tu respuesta de etapas. Considera la información de los resultados de la búsqueda.
        - DEBES incluir citas numéricas en tu respuesta de etapas revisada para asegurar que pueda ser verificada.
        - Agrega una sección de "Referencias" al final de tu respuesta (que no cuenta para el límite de palabras). En forma de:
            - [1] https://ejemplo.com
            - [2] https://ejemplo.com
    - Debes usar la crítica anterior para eliminar información superflua de tu respuesta de etapas.
    Un ejemplo de respuesta revisada de entrada con su crítica correspondiente sería: 
            etapas:
              - Diseño de la Interfaz de Usuario
              - Desarrollo del Backend
              - Integración de Pasarelas de Pago
              - Implementación de Seguridad Web
              - Creación de API para Integraciones Externas
              - Desarrollo del Panel de Administración
              - Pruebas y Aseguramiento de la Calidad
            reflexion:
              falta: Falta incluir una etapa específica para la creación de la base de datos y su integración en el backend.
              sobra: Algunas etapas podrían combinarse para simplificar el proceso, como la integración de pasarelas de pago y la implementación de seguridad web.
            search_queries:
              - Mejores prácticas para el diseño de bases de datos en aplicaciones web
              - Cómo integrar la base de datos en el backend de una aplicación web
              - Estrategias para simplificar la integración de pasarelas de pago y seguridad web en una aplicación web
        Resultados ejemplo de búsquedas: 'Optimiza tus consultas: Las consultas son una parte fundamental de cualquier base de datos, y optimizarlas puede marcar una gran diferencia en el rendimiento de tu aplicación web. Asegúrate de utilizar índices adecuados en tus tablas para acelerar las consultas y evitar búsquedas innecesariamente largas'
    Por lo tanto, un ejemplo de respuesta revisada de salida con su crítica sería:
            etapas:
              - Diseño de la Interfaz de Usuario
              - Desarrollo del Backend
              - Implementación de la Base de Datos y su Integración en el Backend
              - Integración de Servicios Externos y Seguridad
              - Desarrollo del Panel de Administración
              - Pruebas y Aseguramiento de la Calidad
            reflexion:
              falta: Falta una etapa de despliegue
              sobra: Las etapas de la base de datos e integración de servicios externos y seguridad deberían ser parte de Desarrollo del Backend
            search_queries:
                - Cómo desplegar una aplicación web en un servidor
                - Mejores prácticas para el despliegue de aplicaciones web
    Explicación del ejemplo : se han juntado varias etapas como ponía en la crítica, y se ha añadido una etapa específica para la base de datos. Se ha consultado la información adicional para mejorar la respuesta. 
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


def get_revisor(licitacion, requisitos_adicionales, categoria_proyecto, critica_actual, resultados_busqueda):
    first_instructions = revise_instructions.format(
        critica_actual=critica_actual,
        resultados_busqueda=resultados_busqueda,
    )

    prompt_revisor = actor_prompt_template.partial(
        licitacion=licitacion,
        requisitos_adicionales="\n".join(requisitos_adicionales),
        categoria_proyecto=categoria_proyecto,
        first_instruction=first_instructions,
        function_name=ReviseAnswer.__name__,
    )
    model_revisor = model.bind_tools(tools=[ReviseAnswer])

    revision_chain = prompt_revisor | model_revisor
    revision_validator = PydanticToolsParser(tools=[ReviseAnswer])

    revisor = ResponderWithRetries(runnable=revision_chain, validator=revision_validator)
    return revisor

