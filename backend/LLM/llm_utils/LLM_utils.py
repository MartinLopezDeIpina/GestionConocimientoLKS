from langchain.globals import set_debug
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults


def get_model(temperatura=0):
    model = ChatOpenAI(model="gpt-4o-mini", temperature=temperatura, verbose=False)
    set_debug(False)
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

