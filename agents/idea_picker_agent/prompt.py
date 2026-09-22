"""Prompt for selecting ideas from Starter Story and IdeaPicker search results."""

IDEA_SOURCES: list[str] = [
    "https://www.starterstory.com/home",
    "https://ideapicker.io/ideas",
]

_SOURCE_LINES = "\n".join(f"- {source}" for source in IDEA_SOURCES)

SELECT_PROMPT = f"""Extract business ideas from these web search results.

Use only these sources:
{_SOURCE_LINES}

Search results:
{{search_results}}

{{instruction}}

Output format
The output is a list of ideas. Nothing before, nothing after.
Return at most {{limit}} ideas from the search results. Skip duplicates.
Each item is one idea: a short name and a one-sentence description.
"""
