from langchain_openai import OpenAIEmbeddings

from LLM.DB.milvusTools import milvusTools
from config import Config

import os


class modelTools:

    def __init__(self, vectorDB=milvusTools()):
        self.vectorDB = vectorDB

    def get_similar_info(self, input_data):
        embed = get_embedding(input_data)

        similar_resources = self.vectorDB.search_similar_resources(0, embed, RESULTS=3)

        info = ""
        for result in similar_resources:
            info += "\n\nScale metric example: " + result

        return info

    def index_resources(self):
        class Resource:
            pass

        resources_uri = os.path.join(Config.REPO_BASE_FOLDER, "0")

        files = os.listdir(resources_uri)
        for file in files:
            resource = Resource()
            resource.repository_id = 0
            resource.uri = file

            self.vectorDB.index_resource(resource)

            return "Resources indexed"


def get_embedding(text):
    embeddings = OpenAIEmbeddings()
    return embeddings.embed_query(text)
