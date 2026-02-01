"""Table output formatting using Rich."""

from __future__ import annotations

from typing import Any
import json
from datetime import datetime, timezone

from rich.console import Console
from rich.table import Table


def _get_authors(paper: dict[str, Any]) -> str:
    authors = paper.get("authors") or paper.get("author") or paper.get("authorNames")
    if isinstance(authors, list):
        names = []
        for a in authors:
            if isinstance(a, str):
                names.append(a)
            elif isinstance(a, dict):
                names.append(a.get("name") or a.get("author") or "")
        return _truncate_text(", ".join([n for n in names if n]), 72)
    if isinstance(authors, str):
        result = authors
    else:
        result = ""
    return _truncate_text(result, 72)


def _truncate_text(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    if max_len <= 3:
        return text[:max_len]
    return text[: max_len - 3] + "..."


def _get_year(paper: dict[str, Any]) -> str:
    year = paper.get("year") or paper.get("publication_year") or paper.get("conference_year")
    if year is not None:
        return str(year)

    publication_date = paper.get("publication_date")
    if isinstance(publication_date, str) and len(publication_date) >= 4 and publication_date[:4].isdigit():
        return publication_date[:4]
    if isinstance(publication_date, (int, float)):
        try:
            # Handle epoch milliseconds seen in some API payloads.
            ts = float(publication_date)
            if ts > 10_000_000_000:
                ts /= 1000.0
            return str(datetime.fromtimestamp(ts, tz=timezone.utc).year)
        except Exception:
            return ""
    return ""


def _extract_papers(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [d for d in data if isinstance(d, dict)]
    if isinstance(data, dict):
        for key in ("papers", "results", "items", "data", "digest_df"):
            val = data.get(key)
            if isinstance(val, list):
                return [d for d in val if isinstance(d, dict)]
    return []


def _format_scalar(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=True)
    return str(value)


def _format_kv_table(data: dict[str, Any], title: str | None = None) -> str:
    table = Table(title=title)
    table.add_column("Field", overflow="fold")
    table.add_column("Value", overflow="fold")
    for key, value in data.items():
        table.add_row(str(key), _format_scalar(value))
    console = Console()
    with console.capture() as capture:
        console.print(table)
    return capture.get()


def _format_list_table(data: list[Any], title: str | None = None) -> str:
    table = Table(title=title)
    table.add_column("#", justify="right")
    table.add_column("Value", overflow="fold")
    for idx, value in enumerate(data, start=1):
        table.add_row(str(idx), _format_scalar(value))
    console = Console()
    with console.capture() as capture:
        console.print(table)
    return capture.get()


def format_table(data: Any, title: str | None = None) -> str:
    papers = _extract_papers(data)
    if papers:
        table = Table(title=title)
        table.add_column("Title", overflow="fold")
        table.add_column("Authors", overflow="fold")
        table.add_column("Year", justify="right")
        table.add_column("Venue", overflow="fold")
        table.add_column("ID", overflow="fold")

        for p in papers:
            title_val = str(p.get("title") or p.get("paper_title") or "")
            authors_val = _get_authors(p)
            year_val = _get_year(p)
            venue_val = str(p.get("venue") or p.get("conference") or p.get("journal") or "")
            pid = str(
                p.get("paper_id")
                or p.get("paperId")
                or p.get("id")
                or p.get("corpusid")
                or ""
            )
            table.add_row(title_val, authors_val, year_val, venue_val, pid)

        console = Console()
        with console.capture() as capture:
            console.print(table)
        return capture.get()

    if isinstance(data, dict) and data:
        return _format_kv_table(data, title=title)
    if isinstance(data, list) and data:
        return _format_list_table(data, title=title)
    return "(no results)"
