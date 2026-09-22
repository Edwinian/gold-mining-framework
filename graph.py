"""Linear LangGraph pipeline of specialist agents.

The outer graph has one-way edges only. Each node is an agent. Additional
agents can be appended after market_gap_agent later.
"""

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from gold_mining_framework.agents.market_gap_agent import market_gap_agent
from gold_mining_framework.agents.pain_point_agent import pain_point_agent
from gold_mining_framework.agents.reddit_query_agent import reddit_query_agent
from gold_mining_framework.state import AppIdeaState


def build_graph() -> CompiledStateGraph:
    """Compile the linear gold mining framework graph.

    Current topology::

        START -> reddit_query_agent -> pain_point_agent -> market_gap_agent -> END

    Returns:
        Compiled outer graph. Invoke with ``{"query": "<market idea>"}``.
    """
    builder = StateGraph(AppIdeaState)
    builder.add_node("reddit_query_agent", reddit_query_agent)
    builder.add_node("pain_point_agent", pain_point_agent)
    builder.add_node("market_gap_agent", market_gap_agent)
    builder.add_edge(START, "reddit_query_agent")
    builder.add_edge("reddit_query_agent", "pain_point_agent")
    builder.add_edge("pain_point_agent", "market_gap_agent")
    builder.add_edge("market_gap_agent", END)
    return builder.compile()


# Compiled pipeline: START -> reddit_query_agent -> pain_point_agent -> market_gap_agent -> END
graph = build_graph()
