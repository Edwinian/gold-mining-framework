"""Classify a ``--topic`` value for the standalone idea agents."""

MARKETS = frozenset({"health", "wealth", "relationships"})


def classify_topic(topic: str | None) -> tuple[str, str | None]:
    """Return the hierarchy level and the cleaned topic.

    An empty topic means random ideas starting from the market level.
    ``health``, ``wealth``, and ``relationships`` are markets.
    Every other topic is a category.

    Args:
        topic: Raw ``--topic`` value. ``None`` or blank means random.

    Returns:
        ``("random", None)``, ``("market", name)``, or ``("category", name)``.
        Market names are title case.
    """
    cleaned = (topic or "").strip()
    if not cleaned:
        return "random", None
    if cleaned.casefold() in MARKETS:
        return "market", cleaned.title()
    return "category", cleaned
