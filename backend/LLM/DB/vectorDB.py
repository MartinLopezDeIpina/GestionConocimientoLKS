import os
from abc import abstractmethod, ABC

from config import Config


class vectorDB(ABC):
    def __init__(self, host, port):
        self.REPO_BASE_FOLDER = Config.REPO_BASE_FOLDER
        self.COLLECTION_PREFIX = 'collection_'
        self.HOST = host
        self.PORT = port

    @abstractmethod
    def create_instance(self, repository_id):
        pass

    @abstractmethod
    def index_resource(self, resource):
        pass

    @abstractmethod
    def index_json_resource(self, resource):
        pass

    @abstractmethod
    def delete_resource(self, resource):
        pass

    @abstractmethod
    def search_similar_resources(self, repository_id, embed, RESULTS=5):
        pass

    @abstractmethod
    def get_retriever(self, repository_id):
        pass
