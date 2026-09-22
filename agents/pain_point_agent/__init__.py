"""Pain point node for the linear gold mining graph.

Reads Reddit posts from graph state and writes a pain-point analysis string.
This node is invoked by the graph, not as its own command.
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from gold_mining_framework.agents.pain_point_agent.prompt import PROMPT
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


def pain_point_agent(state: AppIdeaState) -> dict:
    """Extract pain points from ``reddit_posts`` into a single analysis string.

    Args:
        state: Graph state. ``reddit_posts`` holds raw Reddit page content.

    Returns:
        An update that sets ``pain_points`` to the analysis text.
    """
    posts = [
        post.strip()
        for post in (state.get("reddit_posts") or [])
        if isinstance(post, str) and post.strip()
    ]
    if not posts:
        return {"pain_points": "No Reddit posts were available to analyze."}

    idea = (state.get("query") or "").strip()
    header = f"Market idea: {idea}\n\n" if idea else ""
    conversations = "\n\n".join(
        f"Reddit post {index}:\n{post}" for index, post in enumerate(posts, start=1)
    )
    response = get_chat_model().invoke(
        [
            SystemMessage(content=PROMPT),
            HumanMessage(content=f"{header}Reddit conversations:\n\n{conversations}"),
        ]
    )
    return {"pain_points": _message_text(response)}


__all__ = ["pain_point_agent"]
