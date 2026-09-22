"""Idea picker agent.

Searches Starter Story and IdeaPicker, then keeps ideas whose Google Trends
line is smoothly upward.

Run it from this project directory:

    python -m idea_picker_agent.invoke --topic=health
"""

import sys
from pathlib import Path

# This directory is the package. Its parent must be on the path when the
# agent is launched from inside the project.
_package_parent = str(Path(__file__).resolve().parents[2])
if _package_parent not in sys.path:
    sys.path.insert(0, _package_parent)

from gold_mining_framework.topic import classify_topic  # noqa: E402

from .harness import run_harness  # noqa: E402

DEFAULT_LIMIT = 20


def idea_picker_agent(state: dict | None = None) -> dict:
    """Pick ideas and return the ones that pass the trend filter.

    Args:
        state: Optional ``topic`` and ``limit`` (default 20). Omit ``topic``
            for random ideas starting from the market level. ``health``,
            ``wealth``, and ``relationships`` are markets. Any other topic is
            a category.

    Returns:
        Dict with ``topic``, ``level``, ``limit``, and ``ideas``. ``ideas``
        contains only the picks that passed ``google_trends_filter``.
    """
    state = state or {}
    raw_topic = state.get("topic")
    topic = raw_topic.strip() if isinstance(raw_topic, str) else None
    level, name = classify_topic(topic)

    raw_limit = state.get("limit", DEFAULT_LIMIT)
    limit = DEFAULT_LIMIT if raw_limit is None else int(raw_limit)

    ideas = run_harness(level, name, limit)
    return {"topic": name, "level": level, "limit": limit, "ideas": ideas}


__all__ = ["idea_picker_agent"]
