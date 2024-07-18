from langchain.globals import set_debug
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults


def get_model():
    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, verbose=True)
    set_debug(True)
    return model


def get_tavily_tool():
    search = TavilySearchAPIWrapper()
    tavily_tool = TavilySearchResults(api_wrapper=search, max_results=5)
    return tavily_tool


def get_tool_name(tool_obj):
    if isinstance(tool_obj, type):
        return tool_obj.__name__
    else:
        return tool_obj.name
