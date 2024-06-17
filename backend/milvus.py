from langchain_community.vectorstores.milvus import Milvus
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
import os
from langchain_openai import OpenAIEmbeddings


def get_embedding(text):
    embeddings = OpenAIEmbeddings()
    return embeddings.embed_query(text)


def get_similar_results(data):
    embedded_data = get_embedding(data)
    similar_resources = search_similar_resources(agent.repository_id, embed, RESULTS=1)

def 
