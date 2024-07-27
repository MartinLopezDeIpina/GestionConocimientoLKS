from langchain_core.prompts import PromptTemplate

from LLM.licitacion_graph.subgrafo_definir_etapas.stagesCustomReflection.EtapasProyecto import EtapasProyecto
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesCustomReflection.EtapasProyectoJustificadas import EtapasProyectoJustificadas
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesCustomReflection.ResponderWithRetries import model


actor_prompt_template = PromptTemplate.from_template(
    """
Eres un agente especializado en determinar las etapas de un proyecto software categorizado como {categoria_proyecto}.
Se debe generar una lista de etapas técnicas típicas para un proyecto software de la categoría {categoria_proyecto} a partir de una licitación y requisitos adicionales.
No serán necesarias etapas de gestión de proyectos como análisis de requisitos o de viabilidad, solo etapas técnicas.
Las etapas deben ser generales, sin entrar en demasiado detalle, aproximadamente entre 3 y 5 etapas. Si las etapas son más que 5 entonces algunas son demasiados esepcíficas. Si son menos de 3, entonces algunas son demasiado generales.
Por ejemplo, para un proyecto de desarrolo de una aplicación web, las etapas podrían ser: diseño, implementación del backend, implementación del frontend, aseguramiento de calidad, despliegue, mantenimiento. También se podrían incluir etapas relacionadas con el dominio si son necesarias.
La licitación es la siguiente: \n{licitacion}
Los requisitos adicionales son: \n{requisitos_adicionales}

{instrucciones_agente}
    """
)

intrucciones_agente_generador ="""
Genera una lista inicial de etapas técnicas para el proyecto software.
"""

instrucciones_agente_generador_con_revision = PromptTemplate.from_template(
    """
Debes modificar la lista de etapas técnicas para el proyecto software basándote en la crítica generada.
Las etapas propuestas son las siguientes: {propuesta_etapas}\n\n
La crítica hacia las etapas propuestas es la siguiente: \n{critica_actual}\n\n
La información adicional es la siguiente: \n{resultados_busqueda}\n\n
Para corregir la respuesta debes seguir los siguientes pasos:
    1- Utiliza el feedback de la sección falta, combinado con la información de los resultados de la búsqueda, para agregar o modificar información importante a tu respuesta de etapas.
    2- Utiliza el feedback de la sección sobra, combinado con la información de los resultados de la búsqueda, para eliminar información superflua de tu respuesta de etapas. Esto puede incluir combinar etapas en una más general.
    3- Anota las referencias de los resultados de búsqueda utilizados para las modificaciones realizadas. Deben enumerados en el siguiente formato para ser citados: '[1] www.paginaejemplo.com/unejemplo', '[2] www.otrapaginaejemplo.com/urlcompleta', tal y como se proporciona en la sección de resultados de búsqueda.
    4- Anota y justifica los cambios realizados en las etapas en la sección de explicación de una forma breve y concisa (una frase por cambio):
        -DEBES Utilizar la información de búsqueda para apoyar tus decisiones.
        -¡¡DEBES SIN FALTA referenciar la información utilizada citando la sección de referencias en la sección de explicación con una notación de citas!! Para ello, si la frase de la explicación ha utilizado alguna fuente de las búsquedas, simplemente pon el número de la referencia: por ejemplo: 
            'Se ha añadido la etapa de implementar consultar nota del examen [1] para asegurar la calidad de la implementación' -> teniendo por ejemplo en la sección de referencias la primera cita: [1] www.paginasobredesarrolloweg.com/algunejemplodecalidad
        -SOLO anota lo modificado y de forma ESPECIFICA, evita ambigüedades como 'se han modificado las etapas siguiendo las críticas', en su lugar: 'se han modificado las etapas x e y haciendo x cambios'.
    """
)


def get_initial_generador(licitacion, requisitos_adicionales, categoria_proyecto):
    generador_prompt = actor_prompt_template.partial(
        licitacion=licitacion,
        requisitos_adicionales="\n".join(requisitos_adicionales),
        categoria_proyecto=categoria_proyecto,
        instrucciones_agente=intrucciones_agente_generador,
    )
    generador_model = model.with_structured_output(EtapasProyecto)

    initial_answer_chain = generador_prompt | generador_model

    return initial_answer_chain


def get_generador(licitacion, requisitos_adicionales, categoria_proyecto,propuesta_etapas, critica_actual, resultados_busqueda):
    resultados_busqueda_formatted = get_resultados_busqueda_formatted(resultados_busqueda, critica_actual.search_queries)

    instrucciones = instrucciones_agente_generador_con_revision.format(propuesta_etapas=propuesta_etapas.etapas, critica_actual=critica_actual, resultados_busqueda=resultados_busqueda_formatted)
    generador_prompt = actor_prompt_template.partial(
        licitacion=licitacion,
        requisitos_adicionales="\n".join(requisitos_adicionales),
        categoria_proyecto=categoria_proyecto,
        critica_actual=critica_actual,
        instrucciones_agente=instrucciones,
    )
    generador_model = model.with_structured_output(EtapasProyectoJustificadas)

    answer_chain = generador_prompt | generador_model

    return answer_chain


def get_resultados_busqueda_formatted(resultados_busqueda, busquedas):
    formatted = ""
    if not busquedas:
        return formatted
    total_busquedas = 1
    for i, busqueda in enumerate(busquedas):
        formatted += f"\tConsulta: {busqueda}\n"
        for j, result in enumerate(resultados_busqueda[i]):
            formatted_result = f"\t\t[{total_busquedas}] {result['url']} contenido: {result['content']} \n"
            formatted += formatted_result
            total_busquedas += 1
    return formatted
