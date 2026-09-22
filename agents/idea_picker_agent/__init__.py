"""Idea picker agent.

Searches Starter Story and IdeaPicker, then keeps ideas whose Google Trends
line is smoothly upward.
"""

from gold_mining_framework.agents.idea_picker_agent.harness import run_harness

DEFAULT_LIMIT = 20


def idea_picker_agent(state: dict | None = None) -> dict:
    """Pick ideas and return the ones that pass the trend filter.

    Args:
        state: Optional ``query`` (default ``None``) and ``limit`` (default 20).
            Omit ``query`` to sample ideas at random.

    Returns:
        Dict with ``query``, ``limit``, and ``ideas``. ``ideas`` contains only
        the picks that passed ``google_trends_filter``.
    """
    state = state or {}
    raw_query = state.get("query")
    query = raw_query.strip() if isinstance(raw_query, str) else None
    query = query or None

    raw_limit = state.get("limit", DEFAULT_LIMIT)
    limit = DEFAULT_LIMIT if raw_limit is None else int(raw_limit)

    ideas = run_harness(query, limit)
    return {"query": query, "limit": limit, "ideas": ideas}


__all__ = ["idea_picker_agent"]
