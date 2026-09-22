"""Landing page node for the linear gold mining graph.

Writes the idea's pain points, market gaps, and a generated HTML page under
``landing_pages``. This node is invoked by the graph, not as its own command.
"""

import re
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from gold_mining_framework.agent_nodes.landing_page_agent.prompt import PROMPT
from gold_mining_framework.llm import get_chat_model
from gold_mining_framework.state import AppIdeaState

_REPO_ROOT = Path(__file__).resolve().parents[2]
LANDING_PAGES_DIR = _REPO_ROOT / "landing_pages"


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


def _snake_case(value: str) -> str:
    """Turn an idea into a filesystem-safe snake_case name.

    Args:
        value: Market idea from graph state.

    Returns:
        Lowercase words joined by underscores.
    """
    slug = re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "idea"


def _html_document(text: str) -> str:
    """Keep only the HTML document if the model wraps it in a code fence.

    Args:
        text: Model reply that should be an HTML document.

    Returns:
        HTML text with a trailing newline.
    """
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[-1]
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()[: stripped.rstrip().rfind("```")]
    return stripped.strip() + "\n"


def landing_page_agent(state: AppIdeaState) -> dict:
    """Write landing-page files for the market idea.

    The idea is the ``query`` field. Files are created at
    ``landing_pages/<idea_in_snake_case>/``.

    Args:
        state: Graph state containing ``query``, ``pain_points``, and
            ``market_gaps``.

    Returns:
        An empty update. The page files are written to disk.
    """
    idea = (state.get("query") or "").strip()
    if not idea:
        msg = "Invoke the graph with {'query': '<market idea>'}."
        raise ValueError(msg)

    pain_points = state.get("pain_points") or ""
    market_gaps = state.get("market_gaps") or ""
    folder_name = _snake_case(idea)
    folder = LANDING_PAGES_DIR / folder_name
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "pain_points.md").write_text(pain_points, encoding="utf-8")
    (folder / "market_gaps.md").write_text(market_gaps, encoding="utf-8")

    response = get_chat_model().invoke(
        [
            SystemMessage(content=PROMPT),
            HumanMessage(
                content=(
                    f"Market idea: {idea}\n\n"
                    f"Pain points:\n{pain_points}\n\n"
                    f"Market gaps:\n{market_gaps}"
                )
            ),
        ]
    )
    html_path = folder / f"{folder_name}.html"
    html_path.write_text(_html_document(_message_text(response)), encoding="utf-8")
    return {}


__all__ = ["landing_page_agent"]
