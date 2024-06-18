from langchain_openai import OpenAIEmbeddings

from config import Config

from LLM.DB import milvusTools as milvusTools, chromaTools
import os


def get_embedding(text):
    embeddings = OpenAIEmbeddings()
    return embeddings.embed_query(text)


def get_similar_info(input_data, db_name):
    embed = get_embedding(input_data)
    if db_name == 'milvus':
        similar_resources = milvusTools.search_similar_resources(0, embed, RESULTS=3)
    elif db_name == 'chroma':
        similar_resources = chromaTools.search_similar_resources(0, embed, RESULTS=3)
    else:
        return "Invalid database name"

    info = ""
    for result in similar_resources:
        info += "\n\nScale metric example: " + result

    return info


def index_resources(db_name):
    class Resource:
        pass

    resources_uri = os.path.join(Config.REPO_BASE_FOLDER, "0")

    files = os.listdir(resources_uri)
    for file in files:
        resource = Resource()
        resource.repository_id = 0
        resource.uri = file

        if db_name == 'milvus':
            milvusTools.index_json_resource(resource)
        elif db_name == 'chroma':
            chromaTools.index_json_resource(resource)
        else:
            return "Invalid database name"
        return "Resources indexed"
