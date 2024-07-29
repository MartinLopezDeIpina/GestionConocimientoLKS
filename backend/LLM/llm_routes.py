import os

from flask import Blueprint, current_app, jsonify

import utils
from LLM.DB.chromaTools import chromaTools
from LLM.DB.modelTools import modelTools
from LLM.licitacion_graph.DatosLicitacion import DatosLicitacion
from LLM.LLMHandler import LLMHandler
from LLM.licitacion_graph.LicitacionGraph import test_start_licitacion_graph, State
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.agente_selector_tecnologias import \
    invoke_seleccionar_tecnologias
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.subgrafo_generacion_lodo_lats import \
    get_lats_generar_candidatos_runnable
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.subgrafo_tecnologias_posibles_herramienta.CRAG_subgrafo_tecnologias_posibles import \
    invoke_tecnologias_posibles_graph
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.subgrafo_tecnologias_posibles_herramienta.subgrafo_proponer_tecnologia_nuevas.subgrafo_proponer_tecnologias_nuevas_graph import \
    invoke_subgrafo_proponer_tecnologia_nueva
from LLM.licitacion_graph.subgrafo_definir_conocimientos.subgrafo_generacion_nodo_lats.subrafo_juntar_herramientas_de_etapa import \
    invoke_subgrafo_juntar_herramientas_de_etapa, HerramientaJuntoTecnologiasPropuestas
from LLM.licitacion_graph.subgrafo_definir_requisitos_tecnicos.RequirementsGraph import invoke_requirements_graph
from LLM.licitacion_graph.subgrafo_definir_requisitos_tecnicos.StageRequirementsReactGraph import invoke_requirements_graph_for_stage
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesCustomReflection.StagesReflectionGraph import start_stages_custom_reflection_graph
from LLM.licitacion_graph.subgrafo_definir_etapas.stagesReflection.StagesReflectionGraph import start_stages_reflection_graph
from LLM.licitacion_graph.subgrafo_definir_conocimientos.LATS_define_kwoledge_graph import invoke_knowledge_graph
from LLM.licitacion_graph.subgrafo_definir_requisitos_tecnicos.StageResult import StageResult
from database import db
from models import NodoArbol

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


# LangGraph #


@llm_blueprint.route('semantic_search/<input_data>')
def semantic_search(input_data):
    nodos = utils.nodo_arbol_semantic_search(input_data)

    nodos_dict = dict()
    for nodo in nodos:
        nodos_dict[nodo.nodoID] = {
            'nodoID': nodo.nodoID,
            'nombre': nodo.nombre,
            'embedding': nodo.embedding.tolist()}

    return jsonify(nodos_dict)


@llm_blueprint.route('test_graph')
def test_graph():
    file_path = os.path.join(current_app.static_folder, 'licitation', 'l1' + '.txt')
    licitacion = utils.read_data_from_file(file_path)
    requisitos_adicionales = []
    test_start_licitacion_graph(licitacion, requisitos_adicionales)
    return 'Ejecutado'


@llm_blueprint.route('test_stage_graph')
def test_stage_graph():
    file_path = os.path.join(current_app.static_folder, 'licitation', 'l1' + '.txt')
    licitacion = utils.read_data_from_file(file_path)
    requisitos_adicionales = []
    categoria_proyecto = 'Desarrollo de aplicación web'

    start_stages_reflection_graph(licitacion, requisitos_adicionales, categoria_proyecto)
    return 'Ejecutado'


@llm_blueprint.route('test_custom_stage_graph')
def test_custom_stage_graph():
    file_path = os.path.join(current_app.static_folder, 'licitation', 'l1' + '.txt')
    licitacion = utils.read_data_from_file(file_path)
    requisitos_adicionales = []
    categoria_proyecto = 'Desarrollo de aplicación web'

    start_stages_custom_reflection_graph(licitacion, requisitos_adicionales, categoria_proyecto)
    return 'Ejecutado'


@llm_blueprint.route('test_react_requirements_agent')
def test_react_requirements_agent():

    file_path = os.path.join(current_app.static_folder, 'licitation', 'l1' + '.txt')
    licitacion = utils.read_data_from_file(file_path)
    requisitos_adicionales = []
    categoria_proyecto = 'Desarrollo de aplicación web'
    etapas_proyecto = ['Diseño', 'Implementación del Frontend']

    datos_licitacion = DatosLicitacion(licitacion=licitacion,
                                       requisitos_adicionales=requisitos_adicionales,
                                       categoria_proyecto=categoria_proyecto,
                                       etapas_proyecto=etapas_proyecto
                                       )

    resultado = invoke_requirements_graph_for_stage(datos_licitacion, 1)

    return 'Ejecutado'


@llm_blueprint.route('test_react_requirements_agent_graph')
def test_react_requirements_agent_graph():
    file_path = os.path.join(current_app.static_folder, 'licitation', 'l1' + '.txt')
    licitacion = utils.read_data_from_file(file_path)
    requisitos_adicionales = []
    categoria_proyecto = 'Desarrollo de aplicación web'
    etapas_proyecto = ['Diseño', 'Implementación del backend', 'Implementación del frontend', 'Aseguramiento de calidad', 'Despliegue', 'Mantenimiento']

    datos_licitacion = DatosLicitacion(
        licitacion=licitacion,
        requisitos_adicionales=requisitos_adicionales,
        categoria_proyecto=categoria_proyecto,
        etapas_proyecto=etapas_proyecto
    )

    invoke_requirements_graph(datos_licitacion)

    return 'Ejecutado'


@llm_blueprint.route('test_tecnologias_posibles_subgraph/<herramienta_necesaria>')
def test_tecnologias_posibles_subgraph(herramienta_necesaria):
    tecnologias = invoke_tecnologias_posibles_graph(herramienta_necesaria)

    tecnologias_dict = dict()
    for tecnologia in tecnologias:
        tecnologias_dict[tecnologia.nodoID] = {
            'nodoID': tecnologia.nodoID,
            'nombre': tecnologia.nombre
        }

    return jsonify(tecnologias_dict)


@llm_blueprint.route('test_subgrafo_proponer_tecnologias_nuevas')
def test_subgrafo_proponer_tecnologias_nuevas():
    herramienta_necesaria = 'Herramienta de gestión de proyectos'
    nodo1: NodoArbol = db.session.query(NodoArbol).filter_by(nodoID=40).first()
    nodo2: NodoArbol = db.session.query(NodoArbol).filter_by(nodoID=37).first()
    nodo3: NodoArbol = db.session.query(NodoArbol).filter_by(nodoID=45).first()
    tecnoligas_rechazadas = [nodo1, nodo2, nodo3]

    invoke_subgrafo_proponer_tecnologia_nueva(herramienta_necesaria, tecnoligas_rechazadas)
    return 'Ejecutado'
    

@llm_blueprint.route('test_subgrafo_tecnologias_posibles_generacion_lats')
def test_subgrafo_tecnologias_posibles_generacion_lats():
    file_path = os.path.join(current_app.static_folder, 'licitation', 'l1' + '.txt')
    licitacion = utils.read_data_from_file(file_path)
    requisitos_adicionales = []
    categoria_proyecto = 'Desarrollo de aplicación web'
    etapas_proyecto = ['Diseño', 'Implementación del backend']

    stage_result_diseno = StageResult('Diseño', 0, ['Herramienta de diseño', 'Herramienta de prototipado'])
    stage_result_backend = StageResult('Implementación del backend', 1, ['Herramienta de gestión de proyectos', 'Herramienta de control de versiones'])
    stage_results = [stage_result_diseno, stage_result_backend]

    datos_licitacion = DatosLicitacion(licitacion=licitacion,
                                       requisitos_adicionales=requisitos_adicionales,
                                       categoria_proyecto=categoria_proyecto,
                                       etapas_proyecto=etapas_proyecto,
                                       requisitos_etapas=stage_results
                                       )

    get_lats_generar_candidatos_runnable().invoke({"datos_licitacion": datos_licitacion})
    return 'Ejecutado'


@llm_blueprint.route('test_subgrafo_juntar_herramientas_de_etapa')
def test_subgrafo_juntar_herramientas_de_etapa():
    herramientas_necesarias = ['patatas fritas', 'patatas cocidas', 'almendras garrapiñadas']
    resultado = invoke_subgrafo_juntar_herramientas_de_etapa(herramientas_necesarias)
    print(resultado)
    return 'Ejecutado'


@llm_blueprint.route('test_agente_selector_tecnologias')
def test_agente_selector_tecnologias():
    file_path = os.path.join(current_app.static_folder, 'licitation', 'l1' + '.txt')
    licitacion = utils.read_data_from_file(file_path)
    requisitos_adicionales = []
    categoria_proyecto = 'Desarrollo de aplicación web'
    etapas_proyecto = ['Diseño', 'Implementación del Frontend']

    t_figma = NodoArbol.query.filter_by(nombre="Figma").first()
    t_UML = NodoArbol.query.filter_by(nombre="UML").first()
    t_react = NodoArbol.query.filter_by(nombre="ReactJS").first()
    t_angular = NodoArbol.query.filter_by(nombre="Angular").first()
    t_vue = NodoArbol.query.filter_by(nombre="Vue.js").first()

    stage_result_diseno = StageResult('Diseño',
                                      0,
                                      ['Herramienta de diseño',
                                       'Herramienta de prototipado'],
                                      [
                                          HerramientaJuntoTecnologiasPropuestas(herramienta='Herramienta de diseño', tecnologias=[t_figma, t_UML]),
                                      ]
                                      )
    stage_result_frontend = StageResult('Implementación del frontend', 2, ['Framework frontend'],
                                        [HerramientaJuntoTecnologiasPropuestas(
                                            herramienta='Framework frontend', tecnologias=[t_react, t_angular, t_vue])])
    stage_results = [stage_result_diseno, stage_result_frontend]

    datos_licitacion = DatosLicitacion(licitacion=licitacion,
                                       requisitos_adicionales=requisitos_adicionales,
                                       categoria_proyecto=categoria_proyecto,
                                       etapas_proyecto=etapas_proyecto,
                                       requisitos_etapas=stage_results
                                       )

    resultado = invoke_seleccionar_tecnologias(datos_licitacion)
    print(resultado)
    return 'Ejecutado'


@llm_blueprint.route('test_lats')
def test_lats():
    file_path = os.path.join(current_app.static_folder, 'licitation', 'l1' + '.txt')
    licitacion = utils.read_data_from_file(file_path)
    requisitos_adicionales = []
    categoria_proyecto = 'Desarrollo de aplicación web'
    etapas_proyecto = ['Diseño', 'Implementación del Frontend', 'Implementación del backend', 'Despliegue']

    t_figma = NodoArbol.query.filter_by(nombre="Figma").first()
    t_UML = NodoArbol.query.filter_by(nombre="UML").first()
    t_react = NodoArbol.query.filter_by(nombre="ReactJS").first()
    t_angular = NodoArbol.query.filter_by(nombre="Angular").first()
    t_vue = NodoArbol.query.filter_by(nombre="Vue.js").first()
    t_spring = NodoArbol.query.filter_by(nombre="Spring Boot").first()
    t_node = NodoArbol.query.filter_by(nombre="Node.js").first()
    t_jsf = NodoArbol.query.filter_by(nombre="JSF").first()
    t_mysql = NodoArbol.query.filter_by(nombre="MySQL").first()
    t_mongo = NodoArbol.query.filter_by(nombre="Mongo DB").first()
    t_docker = NodoArbol.query.filter_by(nombre="Docker").first()
    t_kubernetes = NodoArbol.query.filter_by(nombre="Kubernetes").first()

    stage_result_diseno = StageResult('Diseño',
                                      0,
                                      ['Herramienta de diseño',
                                       'Herramienta de prototipado'],
                                      [
                                          HerramientaJuntoTecnologiasPropuestas(herramienta='Herramienta de diseño', tecnologias=[t_figma, t_UML]),
                                          HerramientaJuntoTecnologiasPropuestas(herramienta='Herramienta de prototipado', tecnologias=[t_figma, t_UML])
                                      ]
                                      )
    stage_result_frontend = StageResult('Implementación del frontend', 2, ['Framework frontend'],
                                        [HerramientaJuntoTecnologiasPropuestas(
                                            herramienta='Framework frontend', tecnologias=[t_react, t_angular, t_vue])
                                        ])
    stage_result_backend = StageResult('Implementación del backend', 3, ['Framework backend', 'Base de datos'],
                                        [
                                            HerramientaJuntoTecnologiasPropuestas(
                                             herramienta='Framework backend', tecnologias=[t_spring, t_node, t_jsf]),
                                            HerramientaJuntoTecnologiasPropuestas(
                                                herramienta='Base de datos', tecnologias=[t_mysql, t_mongo])
                                        ])
    stage_result_despliegue = StageResult('Despliegue', 4, ['Contenedores'],
                                         [HerramientaJuntoTecnologiasPropuestas(
                                             herramienta='Contenedores', tecnologias=[t_docker, t_kubernetes])
                                         ])

    stage_results = [stage_result_diseno, stage_result_frontend, stage_result_backend, stage_result_despliegue]

    datos_licitacion = DatosLicitacion(licitacion=licitacion,
                                       requisitos_adicionales=requisitos_adicionales,
                                       categoria_proyecto=categoria_proyecto,
                                       etapas_proyecto=etapas_proyecto,
                                       requisitos_etapas=stage_results
                                       )

    resultado = invoke_knowledge_graph(datos_licitacion)
    return 'Ejecutado'


