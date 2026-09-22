"""Reddit query node for the linear gold mining graph.

Searches Reddit for a market idea and stores each result's raw page content.
This node is invoked by the graph, not as its own command.
"""

import json

from gold_mining_framework.agents.tools.web_search import web_search
from gold_mining_framework.state import AppIdeaState


def reddit_query_agent(state: AppIdeaState) -> dict:
    """Search Reddit for the market idea and store raw post content.

    Args:
        state: Graph state. ``query`` is the market idea.

    Returns:
        An update that sets ``reddit_posts`` to the raw content of each hit.
    """
    idea = (state.get("query") or "").strip()
    if not idea:
        msg = "Invoke the graph with {'query': '<market idea>'}."
        raise ValueError(msg)

    response = web_search.invoke(
        {
            "query": idea,
            "include_domains": ["reddit.com"],
            "include_domains_mode": "restrict",
            "output_mode": "raw",
            "include_raw_content": True,
        }
    )
    payload = json.loads(response) if isinstance(response, str) else response
    reddit_posts = [
        result["raw_content"]
        for result in payload.get("results") or []
        if result.get("raw_content")
    ]
    return {"reddit_posts": reddit_posts}


__all__ = ["reddit_query_agent"]
