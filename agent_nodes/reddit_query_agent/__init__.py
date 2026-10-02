"""Reddit query node for the linear gold mining graph.

Searches Reddit for a market idea and stores each result's page text.
This node is invoked by the graph, not as its own command.
"""

import json

from gold_mining_framework.agent_nodes.tools.web_search import web_search
from gold_mining_framework.state import AppIdeaState

# Tavily scores Reddit threads for a product name well below the tool's 0.80
# default. A Google search for "<idea> reddit" still returns those threads.
_MIN_REDDIT_SCORE = 0.15


def _post_text(result: dict) -> str:
    """Return the usable text for one Reddit search hit.

    Args:
        result: One Tavily result. Full page text is preferred. Reddit hits
            often have only the snippet in ``content``.

    Returns:
        Title, URL, and body joined by newlines, or an empty string.
    """
    body = (result.get("raw_content") or result.get("content") or "").strip()
    if not body:
        return ""
    title = (result.get("title") or "").strip()
    url = (result.get("url") or "").strip()
    return "\n".join(line for line in (title, url, body) if line)


def reddit_query_agent(state: AppIdeaState) -> dict:
    """Search Reddit for the market idea and store post text.

    The query matches a Google search for the idea plus "reddit": a quoted
    idea restricted to reddit.com. Snippets are kept when the full page is
    missing, because that is the text Google shows for these threads.

    Args:
        state: Graph state. ``query`` is the market idea.

    Returns:
        An update that sets ``query`` to the market idea and ``reddit_posts``
        to the text of each hit.
    """
    idea = (state.get("query") or "").strip()
    if not idea:
        msg = "Invoke the graph with {'query': '<market idea>'}."
        raise ValueError(msg)

    quoted = idea.replace('"', "")
    response = web_search.invoke(
        {
            "query": f'"{quoted}" site:reddit.com',
            "include_domains": ["reddit.com"],
            "include_domains_mode": "restrict",
            "min_relevance_score": _MIN_REDDIT_SCORE,
            "output_mode": "raw",
            "include_raw_content": True,
        }
    )
    payload = json.loads(response) if isinstance(response, str) else response
    reddit_posts = [
        text
        for result in payload.get("results") or []
        if (text := _post_text(result))
    ]
    return {"query": idea, "reddit_posts": reddit_posts}


__all__ = ["reddit_query_agent"]
