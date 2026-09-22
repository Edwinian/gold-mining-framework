"""Direct invocation of the idea generation agent.

Bypasses the outer gold mining graph and runs only this agent.

Usage (from this project directory):
    python -m idea_generation_agent.invoke "Health"
    python -m idea_generation_agent.invoke alternative medicine
"""

import argparse
import logging
import warnings

warnings.filterwarnings("ignore", message="LangSmith now uses UUID v7")

# Package import applies the allowed_objects filter after langchain_core loads.
from gold_mining_framework.agent_nodes.idea_generation_agent import (  # noqa: E402
    idea_generation_agent,
)


def invoke(query: str) -> dict:
    """Run the idea generation agent on a market query.

    Args:
        query: Market, category, or focus area.

    Returns:
        Agent update with ``messages`` and ``market_hierarchy``.
    """
    return idea_generation_agent({"query": query})


def main() -> None:
    """Invoke the idea generation agent from the command line."""
    parser = argparse.ArgumentParser(
        description="Invoke the idea generation agent on a market or focus area."
    )
    parser.add_argument(
        "query",
        nargs="+",
        help="Market segment or focus area, e.g. Health or 'alternative medicine'",
    )
    args = parser.parse_args()
    query = " ".join(args.query)

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.info("Invoking idea generation agent for: %s", query)
    logging.info("This can take several minutes (web search + Google Trends checks).")
    result = invoke(query)
    print(result["market_hierarchy"])  # noqa: T201


if __name__ == "__main__":
    main()
