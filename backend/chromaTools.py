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

from config import Config

REPO_BASE_FOLDER = Config.REPO_BASE_FOLDER
COLLECTION_PREFIX = 'collection_'
HOST = os.getenv("CHROMA_PORT", "localhost")
PORT = os.getenv("CHROMA_PORT", 8000)


def index_json_resource(resource):
    """Indexes a resource by loading its content from a JSON file and adding it to a Chroma collection."""
    with open(os.path.join(REPO_BASE_FOLDER, str(resource.repository_id), resource.uri), 'r') as f:
        data = json.load(f)

    documents = [Document(page_content=str(doc_dict)) for doc_dict in data]

    chroma = create_chroma_instance(resource.repository_id)
    chroma.add_documents(documents)


def create_chroma_instance(repository_id):
    embeddings = OpenAIEmbeddings()
    collection_name = COLLECTION_PREFIX + str(repository_id)

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


def search_similar_resources(repository_id, embed, RESULTS=5):
    """Searches for similar resources in a Chroma collection based on an embedding."""
    chroma = create_chroma_instance(repository_id)
    similar_docs = chroma.similarity_search_by_vector(embed, RESULTS)
    similar_resources = []

    for result in similar_docs:
        similar_resources.append(result.page_content)

    return similar_resources

