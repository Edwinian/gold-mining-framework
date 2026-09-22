"""Direct invocation of the idea picker agent.

Usage (from this project directory):
    python -m idea_picker_agent.invoke --topic=health
    python -m idea_picker_agent.invoke --topic="alternative medicine"
    python -m idea_picker_agent.invoke
"""

import argparse
import logging
import warnings

warnings.filterwarnings("ignore", message="LangSmith now uses UUID v7")

from gold_mining_framework.topic import classify_topic  # noqa: E402

from . import idea_picker_agent  # noqa: E402


def invoke(topic: str | None = None, limit: int = 20) -> dict:
    """Run the idea picker agent.

    Args:
        topic: Optional market or category. Omit it for random ideas starting
            from the market level.
        limit: How many ideas to check before trend filtering. Defaults to 20.

    Returns:
        Agent update with ``topic``, ``level``, ``limit``, and passing
        ``ideas``.
    """
    return idea_picker_agent({"topic": topic, "limit": limit})


def format_ideas(ideas: list[dict]) -> str:
    """Render passing ideas as a list.

    Args:
        ideas: Idea dicts with ``name`` and ``description``.

    Returns:
        A bullet list of ideas, or a short message when none passed.
    """
    if not ideas:
        return "No ideas passed the Google Trends filter."
    lines = []
    for idea in ideas:
        name = idea.get("name") or "Untitled"
        description = (idea.get("description") or "").strip()
        if description:
            lines.append(f"- {name}: {description}")
        else:
            lines.append(f"- {name}")
    return "\n".join(lines)


def main() -> None:
    """Invoke the idea picker agent from the command line."""
    parser = argparse.ArgumentParser(
        description=(
            "Pick ideas from Starter Story and IdeaPicker, then keep the ones "
            "with a smoothly upward Google Trends line. health, wealth, and "
            "relationships are markets. Any other topic is a category. "
            "Omit --topic for random ideas starting from the market level."
        )
    )
    parser.add_argument(
        "--topic",
        default=None,
        help=(
            "Market (health, wealth, relationships) or category. "
            "Omit for random ideas starting from the market level."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="How many ideas to check. Defaults to 20.",
    )
    args = parser.parse_args()
    level, name = classify_topic(args.topic)

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if level == "random":
        logging.info(
            "Invoking idea picker for random ideas from the market level (limit %s)",
            args.limit,
        )
    else:
        logging.info(
            "Invoking idea picker for %s: %s (limit %s)",
            level,
            name,
            args.limit,
        )
    logging.info("This can take several minutes (site search + Google Trends checks).")
    result = invoke(args.topic, args.limit)
    print(format_ideas(result["ideas"]))  # noqa: T201


if __name__ == "__main__":
    main()
