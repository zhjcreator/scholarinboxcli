"""Table output formatting using Rich."""

from __future__ import annotations

from typing import Any

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
        return ", ".join([n for n in names if n])
    if isinstance(authors, str):
        return authors
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


def format_table(data: Any, title: str | None = None) -> str:
    papers = _extract_papers(data)
    if not papers:
        return "(no results)"

    table = Table(title=title)
    table.add_column("Title", overflow="fold")
    table.add_column("Authors", overflow="fold")
    table.add_column("Year", justify="right")
    table.add_column("Venue", overflow="fold")
    table.add_column("ID", overflow="fold")

    for p in papers:
        title_val = str(p.get("title") or p.get("paper_title") or "")
        authors_val = _get_authors(p)
        year_val = str(p.get("year") or p.get("publication_year") or "")
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
