"""Market gap node for the linear gold mining graph.

Reads the pain-point analysis and writes market-gap solutions.
This node is invoked by the graph, not as its own command.
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from gold_mining_framework.agent_nodes.market_gap_agent.prompt import PROMPT
from gold_mining_framework.llm import get_chat_model
from gold_mining_framework.state import AppIdeaState


def _message_text(message: AIMessage) -> str:
    """Extract plain text from an AI message body.

    Args:
        message: Model response that may store content as a string or blocks.

    Returns:
        Concatenated text content.
    """
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text") or ""))
        return "\n".join(part for part in parts if part)
    return str(content)


def market_gap_agent(state: AppIdeaState) -> dict:
    """Turn ``pain_points`` into a market-gap analysis string.

    Args:
        state: Graph state. ``pain_points`` holds the prior analysis.

    Returns:
        An update that sets ``market_gaps`` to the solution analysis.
    """
    pain_points = (state.get("pain_points") or "").strip()
    if not pain_points:
        return {"market_gaps": "No pain points were available to analyze."}

    idea = (state.get("query") or "").strip()
    header = f"Market idea: {idea}\n\n" if idea else ""
    response = get_chat_model().invoke(
        [
            SystemMessage(content=PROMPT),
            HumanMessage(content=f"{header}Pain points:\n\n{pain_points}"),
        ]
    )
    return {"market_gaps": _message_text(response)}


__all__ = ["market_gap_agent"]
