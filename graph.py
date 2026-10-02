"""Linear LangGraph pipeline of specialist agents.

Edges run forward only. If the Reddit search returns no posts, the pipeline
stops and reports that instead of continuing. After the market-gap analysis,
the pain points and market gaps are saved. No landing page is generated.
"""

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from gold_mining_framework.agent_nodes.market_gap_agent import market_gap_agent
from gold_mining_framework.agent_nodes.pain_point_agent import pain_point_agent
from gold_mining_framework.agent_nodes.reddit_query_agent import reddit_query_agent
from gold_mining_framework.idea_validation import save_idea_validation
from gold_mining_framework.state import AppIdeaState


def _has_reddit_posts(state: AppIdeaState) -> bool:
    """Return whether the Reddit search stored any usable post text.

    Args:
        state: Graph state. ``reddit_posts`` holds raw page content.

    Returns:
        True when at least one post has non-empty text.
    """
    return any(
        isinstance(post, str) and post.strip()
        for post in (state.get("reddit_posts") or [])
    )


def _route_after_reddit(state: AppIdeaState) -> str:
    """Choose the next node after the Reddit search.

    Args:
        state: Graph state after ``reddit_query_agent``.

    Returns:
        ``pain_point_agent`` when posts exist, otherwise the stop node.
    """
    if _has_reddit_posts(state):
        return "pain_point_agent"
    return "report_no_reddit_posts"


def report_no_reddit_posts(state: AppIdeaState) -> dict:
    """Stop the pipeline when the Reddit search returned no posts.

    Args:
        state: Graph state. ``query`` is the market idea.

    Returns:
        An update that sets ``halt_message`` for the caller to show.
    """
    idea = (state.get("query") or "").strip() or "this idea"
    return {
        "halt_message": (
            f'No Reddit posts found for "{idea}". '
            "The workflow stopped before pain-point analysis."
        )
    }


def build_graph() -> CompiledStateGraph:
    """Compile the gold mining framework graph.

    Current topology::

        START -> reddit_query_agent -> pain_point_agent -> market_gap_agent
        -> save_idea_validation -> END

        reddit_query_agent -> report_no_reddit_posts -> END
        when the search returns no posts.

    Returns:
        Compiled outer graph. Invoke with ``{"query": "<market idea>"}``.
    """
    builder = StateGraph(AppIdeaState)
    builder.add_node("reddit_query_agent", reddit_query_agent)
    builder.add_node("report_no_reddit_posts", report_no_reddit_posts)
    builder.add_node("pain_point_agent", pain_point_agent)
    builder.add_node("market_gap_agent", market_gap_agent)
    builder.add_node("save_idea_validation", save_idea_validation)
    builder.add_edge(START, "reddit_query_agent")
    builder.add_conditional_edges(
        "reddit_query_agent",
        _route_after_reddit,
        {
            "pain_point_agent": "pain_point_agent",
            "report_no_reddit_posts": "report_no_reddit_posts",
        },
    )
    builder.add_edge("report_no_reddit_posts", END)
    builder.add_edge("pain_point_agent", "market_gap_agent")
    builder.add_edge("market_gap_agent", "save_idea_validation")
    builder.add_edge("save_idea_validation", END)
    return builder.compile()


# Compiled pipeline: START -> reddit_query_agent -> pain_point_agent -> market_gap_agent -> save_idea_validation -> END
# If reddit_query_agent finds no posts: reddit_query_agent -> report_no_reddit_posts -> END
graph = build_graph()
