"""Direct invocation of the idea generation agent.

Usage (from this project directory):
    python -m idea_generation_agent.invoke --topic=health
    python -m idea_generation_agent.invoke --topic="alternative medicine"
    python -m idea_generation_agent.invoke
"""

import argparse
import logging
import warnings

warnings.filterwarnings("ignore", message="LangSmith now uses UUID v7")

from gold_mining_framework.topic import classify_topic  # noqa: E402

from . import idea_generation_agent  # noqa: E402


def invoke(topic: str | None = None) -> dict:
    """Run the idea generation agent for a topic.

    Args:
        topic: Optional market or category. Omit it for random ideas starting
            from the market level.

    Returns:
        Agent update with ``messages``, ``market_hierarchy``, ``topic``, and
        ``level``.
    """
    return idea_generation_agent({"topic": topic})


def main() -> None:
    """Invoke the idea generation agent from the command line."""
    parser = argparse.ArgumentParser(
        description=(
            "Invoke the idea generation agent. health, wealth, and "
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
    args = parser.parse_args()
    level, name = classify_topic(args.topic)

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    if level == "random":
        logging.info(
            "Invoking idea generation agent for random ideas from the market level."
        )
    else:
        logging.info("Invoking idea generation agent for %s: %s", level, name)
    logging.info("This can take several minutes (web search + Google Trends checks).")
    result = invoke(args.topic)
    print(result["market_hierarchy"])  # noqa: T201


if __name__ == "__main__":
    main()
