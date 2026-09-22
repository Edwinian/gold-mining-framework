"""Web search tool for gold mining framework agents."""

import json
import os
from typing import Literal

from langchain_core.tools import tool
from tavily import TavilyClient  # type: ignore[import-untyped]


def _summarize_results(payload: dict) -> str:
    """Turn a Tavily response into compact text for the agent.

    Args:
        payload: Raw Tavily search response.

    Returns:
        A readable summary of the answer and ranked results.
    """
    lines: list[str] = []
    answer = payload.get("answer")
    if answer:
        lines.append(f"Answer: {answer}")
        lines.append("")

    results = payload.get("results") or []
    if not results:
        lines.append("No search results found.")
        return "\n".join(lines)

    lines.append("Results:")
    for i, result in enumerate(results, start=1):
        title = result.get("title") or "Untitled"
        url = result.get("url") or ""
        content = (result.get("content") or "").strip()
        lines.append(f"{i}. {title}")
        if url:
            lines.append(f"   URL: {url}")
        if content:
            lines.append(f"   {content}")
    return "\n".join(lines)


def _format_results(payload: dict, output_mode: Literal["summary", "raw"]) -> str:
    """Return search results as a summary or as raw JSON.

    Args:
        payload: Filtered Tavily search response.
        output_mode: ``summary`` for formatted text, ``raw`` for JSON.

    Returns:
        The formatted summary, or ``json.dumps(payload)`` when the format is raw.
    """
    if output_mode == "raw":
        return json.dumps(payload)
    return _summarize_results(payload)


@tool(parse_docstring=True)
def web_search(
    query: str,
    search_depth: Literal["basic", "advanced", "fast", "ultra-fast"] | None = None,
    topic: Literal["general", "news", "finance"] = "general",
    time_range: Literal["day", "week", "month", "year"] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    days: int | None = None,
    max_hours: int | None = None,
    max_results: int = 20,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
    include_domains_mode: Literal["restrict", "prefer"] | None = None,
    include_answer: bool | Literal["basic", "advanced"] = True,
    include_raw_content: bool | Literal["markdown", "text"] | None = None,
    include_images: bool | None = None,
    timeout: float | None = None,
    country: str | None = None,
    auto_parameters: bool | None = None,
    include_favicon: bool | None = None,
    include_usage: bool | None = None,
    exact_match: bool | None = None,
    fetch_timeout: float | None = None,
    cache_fallback: bool | None = None,
    language: str | None = None,
    filter_by_language: bool | None = None,
    min_relevance_score: float = 0.80,
    output_mode: Literal["summary", "raw"] = "summary",
) -> str:
    """Search the web for current information on a topic.

    Args:
        query: Search query. Be specific.
        search_depth: Search depth. One of basic, advanced, fast, or ultra-fast.
        topic: Result topic. Defaults to general.
        time_range: Limit results to a day, week, month, or year.
        start_date: Include results on or after this date.
        end_date: Include results on or before this date.
        days: Number of days back to search.
        max_hours: Number of hours back to search.
        max_results: Maximum number of results. Defaults to 20.
        include_domains: Domains to include.
        exclude_domains: Domains to exclude.
        include_domains_mode: How include_domains is applied, restrict or prefer.
        include_answer: Include a short answer. Defaults to true.
        include_raw_content: Include raw page content.
        include_images: Include image results.
        timeout: Request timeout in seconds.
        country: Country to boost results for.
        auto_parameters: Let Tavily choose search parameters.
        include_favicon: Include a favicon URL for each result.
        include_usage: Include API credit usage.
        exact_match: Match the query more strictly.
        fetch_timeout: Timeout for fetching page content.
        cache_fallback: Fall back to cached content when a live fetch fails.
        language: Language of the results.
        filter_by_language: Keep only results in the requested language.
        min_relevance_score: Lowest Tavily relevance score to keep. Defaults to 0.80.
        output_mode: ``summary`` returns formatted text. ``raw`` returns the
            filtered Tavily payload as a JSON string. Defaults to summary.

    Returns:
        Search results as a summary, or the raw JSON payload when
        ``output_mode`` is ``raw``.
    """
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError(
            "Tavily is not configured. Set TAVILY_API_KEY in the repo-root .env file."
        )
    options = {
        "search_depth": search_depth,
        "topic": topic,
        "time_range": time_range,
        "start_date": start_date,
        "end_date": end_date,
        "days": days,
        "max_hours": max_hours,
        "max_results": max_results,
        "include_domains": include_domains,
        "exclude_domains": exclude_domains,
        "include_domains_mode": include_domains_mode,
        "include_answer": include_answer,
        "include_raw_content": include_raw_content,
        "include_images": include_images,
        "timeout": timeout,
        "country": country,
        "auto_parameters": auto_parameters,
        "include_favicon": include_favicon,
        "include_usage": include_usage,
        "exact_match": exact_match,
        "fetch_timeout": fetch_timeout,
        "cache_fallback": cache_fallback,
        "language": language,
        "filter_by_language": filter_by_language,
    }
    client = TavilyClient()
    payload = client.search(query, **{key: value for key, value in options.items() if value is not None})
    payload["results"] = [
        result
        for result in payload.get("results") or []
        if float(result.get("score") or 0) >= min_relevance_score
    ]
    return _format_results(payload, output_mode)
