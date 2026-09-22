"""Direct invocation of the idea picker agent.

Usage (from this project directory):
    python -m idea_picker_agent.invoke
    python -m idea_picker_agent.invoke "Health"
    python -m idea_picker_agent.invoke "Health" --limit 10
"""

import argparse
import logging
import warnings

warnings.filterwarnings("ignore", message="LangSmith now uses UUID v7")

from gold_mining_framework.agent_nodes.idea_picker_agent import (  # noqa: E402
    idea_picker_agent,
)


def invoke(query: str | None = None, limit: int = 20) -> dict:
    """Run the idea picker agent.

    Args:
        query: Optional focus. ``None`` samples ideas at random.
        limit: How many ideas to check before trend filtering. Defaults to 20.

    Returns:
        Agent update with ``query``, ``limit``, and passing ``ideas``.
    """
    return idea_picker_agent({"query": query, "limit": limit})


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
            "with a smoothly upward Google Trends line."
        )
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Optional focus, e.g. Health. Omit to sample ideas at random.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="How many ideas to check. Defaults to 20.",
    )
    args = parser.parse_args()
    query = " ".join(args.query).strip() or None

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if query:
        logging.info("Invoking idea picker for: %s (limit %s)", query, args.limit)
    else:
        logging.info("Invoking idea picker with a random sample (limit %s)", args.limit)
    logging.info("This can take several minutes (site search + Google Trends checks).")
    result = invoke(query, args.limit)
    print(format_ideas(result["ideas"]))  # noqa: T201


if __name__ == "__main__":
    main()
