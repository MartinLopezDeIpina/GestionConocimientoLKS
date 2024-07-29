from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def get_modified_messages_chat_prompt_template(template: ChatPromptTemplate, messages: list[BaseMessage]):
    if messages:
        info_prompt = """
        Debes definir lo requierido modificando la siguiente propuesta. Utiliza el feedback proporcionado para ello. Intenta que sea lo más parecido posible al proyecto propuesto, pero ten arregla lo propuesto.
        """

        second_template = ChatPromptTemplate.from_messages([
            ("system", info_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])

        template = template | second_template

    return template

