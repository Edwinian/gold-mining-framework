"""Invoke the idea generation agent from the project directory.

Usage:
    python -m idea_generation_agent.invoke "Health"
    python -m idea_generation_agent.invoke alternative medicine
"""

import sys
from pathlib import Path

# This directory is the gold_mining_framework package. Its parent must be on
# the path so those imports resolve when this module is launched from here.
_package_parent = str(Path(__file__).resolve().parents[1].parent)
if _package_parent not in sys.path:
    sys.path.insert(0, _package_parent)

from gold_mining_framework.agent_nodes.idea_generation_agent.invoke import main

if __name__ == "__main__":
    main()
