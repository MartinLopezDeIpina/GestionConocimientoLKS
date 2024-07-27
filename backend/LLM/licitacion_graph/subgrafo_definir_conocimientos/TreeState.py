from typing_extensions import TypedDict

from LLM.licitacion_graph.DatosLicitacion import DatosLicitacion
from LLM.licitacion_graph.subgrafo_definir_conocimientos.LATS_tree_model import Node


class TreeState(TypedDict):
    # The full tree
    root: Node
    # The original input
    datos_licitacion: DatosLicitacion
