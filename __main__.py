"""CLI entry point for the gold mining graph.

Usage (from the parent of this project directory):
    python -m gold_mining_framework "coparenting"
    python -m gold_mining_framework alternative medicine
"""

import argparse
import logging
import warnings

warnings.filterwarnings("ignore", message="LangSmith now uses UUID v7")

# Package import applies the allowed_objects filter after langchain_core loads.
from gold_mining_framework.graph import graph  # noqa: E402


def main() -> None:
    """Invoke the pipeline with a market query from the command line."""
    parser = argparse.ArgumentParser(
        description="Search Reddit for posts about a market idea."
    )
    parser.add_argument(
        "query",
        nargs="+",
        help="Market idea, e.g. coparenting or 'alternative medicine'",
    )
    args = parser.parse_args()
    query = " ".join(args.query)

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    logging.info("Searching Reddit for: %s", query)
    result = graph.invoke({"query": query})
    posts = result.get("reddit_posts") or []
    print("\n\n".join(posts))  # noqa: T201


if __name__ == "__main__":
    main()
