"""Helpers for sorting paper-like API responses."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _year_from_paper(paper: dict[str, Any]) -> int:
    year = paper.get("year") or paper.get("publication_year") or paper.get("conference_year")
    if isinstance(year, int):
        return year
    if isinstance(year, float):
        return int(year)
    if isinstance(year, str) and year.isdigit():
        return int(year)

    publication_date = paper.get("publication_date")
    if isinstance(publication_date, str) and len(publication_date) >= 4 and publication_date[:4].isdigit():
        return int(publication_date[:4])
    if isinstance(publication_date, (int, float)):
        ts = float(publication_date)
        if ts > 10_000_000_000:
            ts /= 1000.0
        try:
            return datetime.fromtimestamp(ts, tz=timezone.utc).year
        except Exception:
            return 0
    return 0


def sort_paper_response(data: Any, sort_by: str | None, asc: bool) -> Any:
    """Return a sorted copy of known paper-list structures."""
    if not sort_by:
        return data
    if not isinstance(data, dict):
        return data

    for key in ("digest_df", "papers", "results", "items", "data"):
        rows = data.get(key)
        if not isinstance(rows, list) or not rows or not isinstance(rows[0], dict):
            continue

        if sort_by == "year":
            sorted_rows = sorted(rows, key=_year_from_paper, reverse=not asc)
        elif sort_by == "title":
            sorted_rows = sorted(rows, key=lambda p: str(p.get("title") or p.get("paper_title") or "").lower(), reverse=not asc)
        else:
            return data

        out = dict(data)
        out[key] = sorted_rows
        return out
    return data
