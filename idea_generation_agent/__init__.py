"""Idea generation agent.

Run it from this project directory:

    python -m idea_generation_agent.invoke --topic=health
"""

import sys
from pathlib import Path

# This directory is the package. Its parent must be on the path when the
# agent is launched from inside the project.
_package_parent = str(Path(__file__).resolve().parents[2])
if _package_parent not in sys.path:
    sys.path.insert(0, _package_parent)

from gold_mining_framework.topic import classify_topic  # noqa: E402

from .harness import build_harness, run_harness  # noqa: E402

_harness = None


def _user_message(level: str, topic: str | None) -> str:
    """Build the user message for a classified topic.

    Args:
        level: ``random``, ``market``, or ``category``.
        topic: Cleaned topic. ``None`` when the level is random.

    Returns:
        Instruction the idea generation model should follow.
    """
    if level == "random":
        return (
            "Level: random\n"
            "Generate random ideas starting from the market level across "
            "Health, Wealth, and Relationships."
        )
    if level == "market":
        return (
            f"Level: market\nTopic: {topic}\n"
            f"Generate categories, subcategories, and sub-niches under the "
            f"{topic} market only."
        )
    return (
        f"Level: category\nTopic: {topic}\n"
        "Start with this category and only generate the subcategories and "
        "sub-niches underneath it."
    )


def idea_generation_agent(state: dict | None = None) -> dict:
    """Run the idea generation agent for a topic.

    Args:
        state: Optional ``topic``. Omit it, or leave it blank, for random
            ideas starting from the market level. ``health``, ``wealth``, and
            ``relationships`` are markets. Any other topic is a category.
    """
    global _harness
    if _harness is None:
        _harness = build_harness()

    state = state or {}
    raw_topic = state.get("topic")
    topic = raw_topic.strip() if isinstance(raw_topic, str) else None
    level, name = classify_topic(topic)
    messages, hierarchy = run_harness(_user_message(level, name), _harness)
    return {"messages": messages, "market_hierarchy": hierarchy, "topic": name, "level": level}


__all__ = ["idea_generation_agent"]
