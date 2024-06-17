from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from config import Config

import milvusTools as milvusTools
import os


def get_embedding(text):
    embeddings = OpenAIEmbeddings()
    return embeddings.embed_query(text)


def get_similar_info(input_data):
    embed = get_embedding(input_data)
    similar_resources = milvusTools.search_similar_resources(0, embed, RESULTS=3)
    info = ""
    for result in similar_resources:
        # print(result)
        # info += "\n\nINFO CHUNK: " + result[0].page_content  + "\nSource: " + result[0].metadata["source"] + " page:" + str(result[0].metadata["page"]) + "\n\n"
        info += "\n\nINFO CHUNK: " + result[0].page_content

    return info


def index_resources():
    resources_uri = Config.REPO_BASE_FOLDER

    files = os.listdir(resources_uri)
    for file in files:
        milvusTools.index_resource(file)


