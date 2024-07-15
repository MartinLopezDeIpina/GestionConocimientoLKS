import os

from flask import Blueprint, current_app

import utils
from LLM.DB.chromaTools import chromaTools
from LLM.DB.modelTools import modelTools
from LLM.LLMHandler import LLMHandler
from LLM.LicitacionGraph import test_start_licitacion_graph

llm_blueprint = Blueprint('llm', __name__)


@llm_blueprint.route('test/<nombre_fichero>')
def llm_test(nombre_fichero):
    file_path = os.path.join(current_app.static_folder, 'CV', nombre_fichero+'.txt')
    input_data = utils.read_data_from_file(file_path)
    llmHandler = LLMHandler()
    return llmHandler.handle_knowledges(input_data=input_data)


@llm_blueprint.route('count_parents_of_leafs')
def count_parents_of_leafs():
    return str(utils.count_parents_of_leafs())


@llm_blueprint.route('get_similar_info_from_vector/<input_data>')
def get_similar_info(input_data):
    model_tools = modelTools()
    return model_tools.get_similar_info(input_data)


@llm_blueprint.route('add_vector_files')
def add_vector_files():
    model_tools = modelTools()
    return model_tools.index_resources()


@llm_blueprint.route('get_knowledge_level/<cv_file>/<skills_file>')
def get_knowledge_level(cv_file, skills_file):
    llm = LLMHandler()

    cv_path = os.path.join(current_app.static_folder, 'CV', cv_file+'.txt')
    cv_data = utils.read_data_from_file(cv_path)

    skills_path = os.path.join(current_app.static_folder, 'CV', skills_file+'.json')
    skills_data = utils.read_data_from_file(skills_path)

    return llm.handle_knowledge_level(cv_data, skills_data)


@llm_blueprint.route('add_chroma_files')
def add_chroma_files():
    model_tools = modelTools(chromaTools())
    return model_tools.index_resources()


@llm_blueprint.route('get_similar_info_from_vector_chroma/<input_data>')
def get_similar_info_chroma(input_data):
    model_tools = modelTools(chromaTools())
    return model_tools.get_similar_info(input_data)


@llm_blueprint.route('tavily_search/<input_data>')
def tavily_search(input_data):
    llm = LLMHandler()
    return llm.handle_try_tavily_search(input_data)


@llm_blueprint.route('handle_knowledge_metric_reaact/<input_data>')
async def handle_knowledge_metric_reaact(input_data):
    llm = LLMHandler()
    return await llm.handle_knowledge_metric_reaact(input_data)


@llm_blueprint.route('test_graph')
def test_graph():
    test_start_licitacion_graph()
    return 'Ejecutado'

