"""Google Trends filter: search an idea, then judge if the trend rises smoothly."""

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from gold_mining_framework.llm import get_chat_model
from gold_mining_framework.agent_nodes.tools.web_search import web_search

# Small model used only to judge a trend snippet. The pipeline agents keep grok-4.7.
SMALL_MODEL = "xai:grok-3-mini"

_JUDGE_PROMPT = """Decide if this idea's Google Trends line is smoothly upward.

Idea: {idea}

Worldwide Google Trends since 2004, from web search:
{search_results}

Smoothly upward means a steady rise from 2004 to the present.
Flat, declining, highly volatile, or unclear trends are not smoothly upward.
"""


class _SmoothTrend(BaseModel):
    """Judgment of whether a Google Trends line rises smoothly."""

    smoothly_upward: bool = Field(
        description="True only when the worldwide trend since 2004 rises smoothly."
    )


_judge = None


def _trend_judge():
    """Return a small model that answers with a boolean trend judgment."""
    global _judge
    if _judge is None:
        _judge = get_chat_model(model=SMALL_MODEL).with_structured_output(_SmoothTrend)
    return _judge


@tool(parse_docstring=True)
def google_trends_filter(idea: str) -> bool:
    """Check whether an idea's Google Trends line is smoothly upward.

    Search the web for the idea's worldwide Google Trends since 2004, then
    ask a small model whether that trend rises smoothly.

    Args:
        idea: Market idea to check.

    Returns:
        True when the worldwide trend since 2004 is smoothly upward.
    """
    cleaned = idea.strip()
    if not cleaned:
        return False

    search_results = web_search.invoke(
        {"query": f"{cleaned} Google Trends worldwide since 2004"}
    )
    decision = _trend_judge().invoke(
        [
            HumanMessage(
                content=_JUDGE_PROMPT.format(
                    idea=cleaned,
                    search_results=search_results,
                )
            )
        ]
    )
    if isinstance(decision, dict):
        return bool(decision.get("smoothly_upward"))
    return bool(decision.smoothly_upward)
