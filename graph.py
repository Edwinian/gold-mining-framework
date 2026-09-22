"""Linear LangGraph pipeline of specialist agents.

The outer graph has one-way edges only. Each node is an agent. Additional
agents can be appended after reddit_query_agent later.
"""

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from gold_mining_framework.agents.reddit_query_agent import reddit_query_agent
from gold_mining_framework.state import AppIdeaState


def build_graph() -> CompiledStateGraph:
    """Compile the linear gold mining framework graph.

    Current topology::

        START -> reddit_query_agent -> END

    Returns:
        Compiled outer graph. Invoke with ``{"query": "<market idea>"}``.
    """
    builder = StateGraph(AppIdeaState)
    builder.add_node("reddit_query_agent", reddit_query_agent)
    builder.add_edge(START, "reddit_query_agent")
    builder.add_edge("reddit_query_agent", END)
    return builder.compile()


# Compiled pipeline: START -> reddit_query_agent -> END
graph = build_graph()
