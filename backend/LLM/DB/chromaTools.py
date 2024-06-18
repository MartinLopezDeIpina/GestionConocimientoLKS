import json
import os

from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
import uuid

import chromadb
from chromadb.config import Settings, DEFAULT_TENANT, DEFAULT_DATABASE

from LLM.DB.vectorDB import vectorDB
from config import Config


class chromaTools(vectorDB):

    def __init__(self):
        super().__init__(host="localhost", port=8000)

    def index_json_resource(self, resource):
        """Indexes a resource by loading its content from a JSON file and adding it to a Chroma collection."""
        with open(os.path.join(self.REPO_BASE_FOLDER, str(resource.repository_id), resource.uri), 'r') as f:
            data = json.load(f)

        documents = [Document(page_content=str(doc_dict)) for doc_dict in data]

        chroma = self.create_instance(resource.repository_id)
        chroma.add_documents(documents)

    def create_instance(self, repository_id):
        embeddings = OpenAIEmbeddings()
        collection_name = self.COLLECTION_PREFIX + str(repository_id)

        chroma_client = chromadb.HttpClient(
            host="localhost",
            port=8000,
            ssl=False,
            headers=None,
            settings=Settings(),
            tenant=DEFAULT_TENANT,
            database=DEFAULT_DATABASE,
        )
        langchain_chroma = Chroma(
            client=chroma_client,
            collection_name=collection_name,
            embedding_function=embeddings,
        )
        return langchain_chroma

    def search_similar_resources(self, repository_id, embed, RESULTS=5):
        """Searches for similar resources in a Chroma collection based on an embedding."""
        chroma = self.create_instance(repository_id)
        similar_docs = chroma.similarity_search_by_vector(embed, RESULTS)
        similar_resources = []

        for result in similar_docs:
            similar_resources.append(result.page_content)

        return similar_resources

    def delete_resource(self, resource):
        pass

    def index_resource(self, resource):
        pass

    def get_retriever(self, repository_id):
        pass

