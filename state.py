"""State schema for the linear gold mining framework graph."""

from typing import Annotated, NotRequired

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AppIdeaState(TypedDict):
    """Shared state passed along the linear agent pipeline.

    Attributes:
        query: Market idea. The Reddit query agent writes the trimmed idea here.
        messages: Conversation trace for agent nodes that keep a message history.
        market_hierarchy: Validated market / category / niche tree from the
            Market Idea Generator.
        reddit_posts: Raw content of Reddit pages found for the market idea.
        pain_points: Pain-point analysis written from those Reddit posts.
        market_gaps: Solution and market-gap analysis written from those pain points.
    """

    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    market_hierarchy: NotRequired[str]
    reddit_posts: NotRequired[list[str]]
    pain_points: NotRequired[str]
    market_gaps: NotRequired[str]
