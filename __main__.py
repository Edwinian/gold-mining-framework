"""CLI entry point for the gold mining graph.

Usage (from this project directory):
    python -m gold_mining_framework --idea=coparenting
    python -m gold_mining_framework --idea "alternative medicine"
"""

import argparse
import logging
import sys
import warnings
from pathlib import Path

# This directory is the package. Its parent must be on the path when the
# command is launched from inside the project.
_package_parent = str(Path(__file__).resolve().parent.parent)
if _package_parent not in sys.path:
    sys.path.insert(0, _package_parent)

warnings.filterwarnings("ignore", message="LangSmith now uses UUID v7")

from gold_mining_framework.graph import graph  # noqa: E402


def main() -> None:
    """Invoke the pipeline with a market idea from the command line."""
    parser = argparse.ArgumentParser(
        description="Search Reddit for posts about a market idea."
    )
    parser.add_argument(
        "--idea",
        required=True,
        help="Market idea, e.g. --idea=coparenting",
    )
    args = parser.parse_args()
    idea = args.idea.strip()
    if not idea:
        parser.error("--idea must not be empty")

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logging.info("Searching Reddit for: %s", idea)
    result = graph.invoke({"query": idea})
    posts = result.get("reddit_posts") or []
    print("\n\n".join(posts))  # noqa: T201


if __name__ == "__main__":
    main()
