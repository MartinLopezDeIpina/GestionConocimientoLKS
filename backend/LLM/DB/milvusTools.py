from langchain_community.vectorstores.milvus import Milvus
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
import os
import json

from LLM.DB.vectorDB import vectorDB
from config import Config


class milvusTools(vectorDB):

    def __init__(self):
        super().__init__(host="localhost", port=19530)

    def create_instance(self, repository_id):
        embeddings = OpenAIEmbeddings()
        collection_name = self.COLLECTION_PREFIX + str(repository_id)
        return Milvus(embeddings, collection_name=collection_name, connection_args={"host": self.HOST, "port": self.PORT}, auto_id=True)

    def index_resource(self, resource):
        """Indexes a resource by loading its content, splitting it into chunks, and adding it to a Milvus collection."""
        loader = PyPDFLoader(os.path.join(self.REPO_BASE_FOLDER, str(resource.repository_id), resource.uri), extract_images=False)
        pages = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=10, chunk_overlap=0)
        docs = text_splitter.split_documents(pages)
        milvus = self.create_instance(resource.repository_id)
        milvus.add_documents(docs)

    def index_json_resource(self, resource):
        """Indexes a resource by loading its content from a JSON file and adding it to a Milvus collection."""
        with open(os.path.join(self.REPO_BASE_FOLDER, str(resource.repository_id), resource.uri), 'r') as f:
            data = json.load(f)

        documents = [Document(page_content=str(doc_dict)) for doc_dict in data]

        milvus = self.create_instance(resource.repository_id)
        milvus.add_documents(documents)

    def delete_resource(self, resource):
        """Deletes a resource from a Milvus collection based on its source."""
        milvus = self.create_instance(resource.repository_id)
        expr = f"source == '{self.REPO_BASE_FOLDER}/{resource.repository_id}/{resource.uri}'"
        milvus.delete(expr=expr)

    def search_similar_resources(self, repository_id, embed, RESULTS=5):
        """Searches for similar resources in a Milvus collection based on an embedding."""
        milvus = self.create_instance(repository_id)
        similar_docs = milvus.similarity_search_with_score_by_vector(embed, RESULTS)

        similar_resources = []

        for result in similar_docs:
            similar_resources.append(result[0].page_content)

        return similar_resources

    def get_retriever(self, repository_id):
        milvus = self.create_instance(repository_id)
        return milvus.as_retriever()
