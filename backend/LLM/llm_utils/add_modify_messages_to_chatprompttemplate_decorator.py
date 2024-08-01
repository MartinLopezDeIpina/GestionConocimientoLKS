from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def get_modified_messages_chat_prompt_template(template: ChatPromptTemplate, messages: list[BaseMessage]):
    if messages:
        info_prompt = """
        Debes definir lo requierido modificando la siguiente propuesta. Utiliza el feedback proporcionado para ello. Intenta que sea lo más parecido posible al proyecto propuesto, pero ten arregla lo propuesto.
        """

        template.append(("system", info_prompt))
        template.append(MessagesPlaceholder(variable_name="mensajes_modificacion"))

    return template

