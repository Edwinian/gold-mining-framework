"""Pick ideas from Starter Story and IdeaPicker, then keep upward trends."""

import logging
import os
import random
from urllib.parse import urlparse

from pydantic import BaseModel, Field
from tavily import TavilyClient  # type: ignore[import-untyped]

from gold_mining_framework.agent_nodes.idea_picker_agent.prompt import (
    IDEA_SOURCES,
    SELECT_PROMPT,
)
from gold_mining_framework.agent_nodes.tools.google_trends_filter import (
    google_trends_filter,
)
from gold_mining_framework.llm import get_chat_model
from gold_mining_framework.agent_nodes.tools.web_search import _summarize_results

logger = logging.getLogger(__name__)


class PickedIdea(BaseModel):
    """One business idea taken from a source page."""

    name: str
    description: str
    source: str = Field(description="Page URL the idea came from.")


class PickedIdeas(BaseModel):
    """Ideas selected from the search results."""

    ideas: list[PickedIdea]


def _source_domain(url: str) -> str:
    """Return the registrable host used to restrict a Tavily search."""
    host = urlparse(url).netloc.removeprefix("www.")
    return host


def _search_idea_sites(query: str | None, limit: int) -> str:
    """Search Starter Story and IdeaPicker for candidate ideas.

    Args:
        query: Optional focus. A broad ideas query is used when this is omitted.
        limit: How many ideas the caller wants, used to size each search.

    Returns:
        Combined search text from both sources.
    """
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError(
            "Tavily is not configured. Set TAVILY_API_KEY in the repo-root .env file."
        )

    focus = query or "startup business ideas"
    client = TavilyClient()
    max_results = min(20, max(limit, 8))
    sections: list[str] = []
    for source in IDEA_SOURCES:
        logger.info("web_search: %s %s", focus, source)
        payload = client.search(
            query=f"{focus} {source}",
            max_results=max_results,
            include_answer=True,
            include_domains=[_source_domain(source)],
            include_domains_mode="restrict",
            topic="general",
        )
        sections.append(f"Source: {source}\n{_summarize_results(payload)}")
    return "\n\n".join(sections)


def _select_ideas(query: str | None, limit: int, search_results: str) -> list[PickedIdea]:
    """Choose up to ``limit`` ideas from the search results.

    A query keeps the most relevant ideas. Without a query, a larger pool is
    extracted and ``limit`` ideas are sampled at random.

    Args:
        query: Optional focus area. ``None`` selects at random.
        limit: Maximum number of ideas to return before trend filtering.
        search_results: Combined text from both idea sources.

    Returns:
        Selected ideas, at most ``limit`` of them.
    """
    pool_size = limit if query else max(limit * 2, limit)
    if query:
        instruction = (
            f"Choose the ideas most relevant to this query: {query}."
        )
    else:
        instruction = (
            "List distinct ideas that appear in the results, spread across both sources."
        )
    selector = get_chat_model().with_structured_output(PickedIdeas)
    decision = selector.invoke(
        SELECT_PROMPT.format(
            search_results=search_results,
            instruction=instruction,
            limit=pool_size,
        )
    )
    ideas = decision.ideas if isinstance(decision, PickedIdeas) else [
        PickedIdea.model_validate(item) for item in decision.get("ideas", [])
    ]

    unique: list[PickedIdea] = []
    seen: set[str] = set()
    for idea in ideas:
        key = idea.name.strip().casefold()
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(idea)

    if query is None and len(unique) > limit:
        return random.sample(unique, limit)
    return unique[:limit]


def _passes_trend_filter(idea: PickedIdea) -> bool:
    """Return whether ``google_trends_filter`` accepts this idea."""
    logger.info("google_trends_filter: %s", idea.name)
    result = google_trends_filter.invoke({"idea": idea.name})
    if isinstance(result, bool):
        return result
    return str(result).strip().lower() == "true"


def run_harness(query: str | None, limit: int = 20) -> list[dict]:
    """Search both idea sites, pick ideas, and keep upward Google Trends.

    Args:
        query: Optional focus. ``None`` samples ideas at random.
        limit: How many ideas to check. Defaults to 20.

    Returns:
        Ideas that passed ``google_trends_filter``, each as a dict with
        ``name``, ``description``, and ``source``.
    """
    if limit < 1:
        raise ValueError("limit must be at least 1.")

    search_results = _search_idea_sites(query, limit)
    selected = _select_ideas(query, limit, search_results)
    logger.info("Checking %s ideas against Google Trends.", len(selected))

    passed: list[dict] = []
    for idea in selected:
        if not _passes_trend_filter(idea):
            continue
        passed.append(idea.model_dump())
        logger.info("Kept: %s", idea.name)
    logger.info("%s ideas passed the trend filter.", len(passed))
    return passed
