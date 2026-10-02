"""Save idea-validation files for a market idea.

Writes the pain-point and market-gap analyses. No page is generated.
"""

import re
from pathlib import Path

from gold_mining_framework.state import AppIdeaState

_REPO_ROOT = Path(__file__).resolve().parent
IDEA_VALIDATIONS_DIR = _REPO_ROOT / "idea_validations"


def _snake_case(value: str) -> str:
    """Turn an idea into a filesystem-safe snake_case name.

    Args:
        value: Market idea from graph state.

    Returns:
        Lowercase words joined by underscores.
    """
    slug = re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "idea"


def save_idea_validation(state: AppIdeaState) -> dict:
    """Write the pain-point and market-gap analyses for the market idea.

    The idea is the ``query`` field. Files are created at
    ``idea_validations/<idea_in_snake_case>/``.

    Args:
        state: Graph state containing ``query``, ``pain_points``, and
            ``market_gaps``.

    Returns:
        An empty update. The analysis files are written to disk.
    """
    idea = (state.get("query") or "").strip()
    if not idea:
        msg = "Invoke the graph with {'query': '<market idea>'}."
        raise ValueError(msg)

    folder = IDEA_VALIDATIONS_DIR / _snake_case(idea)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "pain_points.md").write_text(
        state.get("pain_points") or "",
        encoding="utf-8",
    )
    (folder / "market_gaps.md").write_text(
        state.get("market_gaps") or "",
        encoding="utf-8",
    )
    return {}
