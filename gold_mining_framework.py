"""Run the graph from this project directory.

Usage:
    python -m gold_mining_framework --idea=coparenting
"""

import runpy
import sys
from pathlib import Path

_package_parent = str(Path(__file__).resolve().parent.parent)
if _package_parent not in sys.path:
    sys.path.insert(0, _package_parent)

# Drop this launcher so the real package can be imported.
sys.path = [entry for entry in sys.path if Path(entry or ".").resolve() != Path(__file__).resolve().parent]

runpy.run_module("gold_mining_framework", run_name="__main__")
