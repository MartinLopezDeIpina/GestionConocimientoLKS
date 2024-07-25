import json
from langchain_core.messages import ToolMessage
from langchain_core.output_parsers import JsonOutputToolsParser
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from collections import defaultdict
from LLM.licitacion_graph.subgrafo_definir_conocimientos.LATS_tree_model import Node
from LLM.licitacion_graph.subgrafo_definir_conocimientos.TreeState import TreeState
from LLM.llm_utils.LLM_utils import get_tavily_tool, get_model
from LLM.licitacion_graph.subgrafo_definir_conocimientos.LATS_reflection import reflection_chain
from typing import Literal
from langgraph.graph import END, StateGraph, START

llm = get_model()

tavily_tool = get_tavily_tool()
tools = [tavily_tool]
tool_executor = ToolExecutor(tools)

parser = JsonOutputToolsParser(return_id=True)


prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an AI assistant.",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="messages", optional=True),
    ]
)


initial_answer_chain = prompt_template | llm.bind_tools(tools=tools).with_config(
    run_name="GenerateInitialCandidate"
)


def generate_initial_response(state: TreeState) -> dict:
    """Generate the initial candidate response."""
    res = initial_answer_chain.invoke({"input": state["input"]})
    parsed = parser.invoke(res)
    tool_responses = tool_executor.batch(
        [ToolInvocation(tool=r["type"], tool_input=r["args"]) for r in parsed]
    )
    output_messages = [res] + [
        ToolMessage(content=json.dumps(resp), tool_call_id=tool_call["id"])
        for resp, tool_call in zip(tool_responses, parsed)
    ]
    reflection = reflection_chain.invoke(
        {"input": state["input"], "candidate": output_messages}
    )
    root = Node(output_messages, reflection=reflection)
    return {
        **state,
        "root": root,
    }


# This generates N candidate values
# for a single input to sample actions from the environment
def generate_candidates(messages: ChatPromptValue, config: RunnableConfig):
    #De default venía a 5
    n = config["configurable"].get("N", 5)
    bound_kwargs = llm.bind_tools(tools=tools).kwargs
    chat_result = llm.generate(
        [messages.to_messages()],
        n=n,
        callbacks=config["callbacks"],
        run_name="GenerateCandidates",
        **bound_kwargs,
    )
    return [gen.message for gen in chat_result.generations[0]]


expansion_chain = prompt_template | generate_candidates


def expand(state: TreeState, config: RunnableConfig) -> dict:
    """Starting from the "best" node in the tree, generate N candidates for the next step."""
    root = state["root"]
    best_candidate: Node = root.best_child if root.children else root
    messages = best_candidate.get_trajectory()
    # Generate N candidates from the single child candidate
    new_candidates = expansion_chain.invoke(
        {"input": state["input"], "messages": messages}, config
    )
    parsed = parser.batch(new_candidates)
    flattened = [
        (i, tool_call)
        for i, tool_calls in enumerate(parsed)
        for tool_call in tool_calls
    ]
    tool_responses = tool_executor.batch(
        [
            ToolInvocation(tool=tool_call["type"], tool_input=tool_call["args"])
            for _, tool_call in flattened
        ]
    )
    collected_responses = defaultdict(list)
    for (i, tool_call), resp in zip(flattened, tool_responses):
        collected_responses[i].append(
            ToolMessage(content=json.dumps(resp), tool_call_id=tool_call["id"])
        )
    output_messages = []
    for i, candidate in enumerate(new_candidates):
        output_messages.append([candidate] + collected_responses[i])

    # Reflect on each candidate
    # For tasks with external validation, you'd add that here.
    reflections = reflection_chain.batch(
        [{"input": state["input"], "candidate": msges} for msges in output_messages],
        config,
    )
    # Grow tree
    child_nodes = [
        Node(cand, parent=best_candidate, reflection=reflection)
        for cand, reflection in zip(output_messages, reflections)
    ]
    best_candidate.children.extend(child_nodes)
    # We have already extended the tree directly, so we just return the state
    return state


def should_loop(state: TreeState) -> Literal["expand", "__end__"]:
    """Determine whether to continue the tree search."""
    root = state["root"]
    if root.is_solved:
        return END
    if root.height > 5:
        return END
    return "expand"


def invoke_knowledge_graph(input_question: str):
    builder = StateGraph(TreeState)
    builder.add_node("start", generate_initial_response)
    builder.add_node("expand", expand)
    builder.add_edge(START, "start")

    builder.add_conditional_edges(
        "start",
        # Either expand/rollout or finish
        should_loop,
    )
    builder.add_conditional_edges(
        "expand",
        # Either continue to rollout or finish
        should_loop,
    )

    graph = builder.compile()

    last_step = None
    for step in graph.stream({"input": input_question}):
        last_step = step
        step_name, step_state = next(iter(step.items()))
        print(step_name)
        print("rolled out: ", step_state["root"].height)
        print("---")

    if "expand" in last_step:
        solution_node = last_step["expand"]["root"].get_best_solution()
        best_trajectory = solution_node.get_trajectory(include_reflections=False)
        print(best_trajectory[-1].content)
    else:
        print(f"last step: {last_step}")

    # TODO: esto no sé si está bien mirarlo cuando acabes el grafo lats
    return last_step
