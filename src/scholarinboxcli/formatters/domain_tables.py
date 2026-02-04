"""Domain-specific table formatters for non-paper responses."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.table import Table

from scholarinboxcli.formatters.table import format_table


def _render(table: Table) -> str:
    console = Console()
    with console.capture() as capture:
        console.print(table)
    return capture.get()


def format_auth_status(data: Any, title: str | None = None) -> str:
    if not isinstance(data, dict):
        return format_table(data, title)
    table = Table(title=title)
    table.add_column("Field", overflow="fold")
    table.add_column("Value", overflow="fold")
    for key, value in data.items():
        table.add_row(str(key), str(value))
    return _render(table)


def format_collection_list(data: Any, title: str | None = None) -> str:
    if isinstance(data, list) and data and isinstance(data[0], str):
        table = Table(title=title)
        table.add_column("#", justify="right")
        table.add_column("Name", overflow="fold")
        for i, name in enumerate(data, start=1):
            table.add_row(str(i), str(name))
        return _render(table)

    if isinstance(data, list) and data and isinstance(data[0], dict):
        table = Table(title=title)
        table.add_column("ID", overflow="fold")
        table.add_column("Name", overflow="fold")
        for item in data:
            cid = item.get("id") or item.get("collection_id") or ""
            name = item.get("name") or item.get("collection_name") or ""
            table.add_row(str(cid), str(name))
        return _render(table)

    if isinstance(data, dict) and "expanded_collections" in data:
        return format_collection_list(data.get("expanded_collections"), title)

    return format_table(data, title)


def format_conference_list(data: Any, title: str | None = None) -> str:
    rows = data.get("conferences") if isinstance(data, dict) else None
    if isinstance(rows, list):
        table = Table(title=title)
        table.add_column("ID", justify="right")
        table.add_column("Short")
        table.add_column("Dates")
        table.add_column("URL")
        for row in rows:
            cid = row.get("conference_id", "")
            short = row.get("short_title") or row.get("full_title") or ""
            start = row.get("start_date") or ""
            end = row.get("end_date") or ""
            dates = f"{start} -> {end}" if (start or end) else ""
            url = row.get("conference_url") or ""
            table.add_row(str(cid), str(short), str(dates), str(url))
        return _render(table)
    return format_table(data, title)


def format_conference_explore(data: Any, title: str | None = None) -> str:
    rows = data.get("conf_data_list") if isinstance(data, dict) else None
    if isinstance(rows, list):
        table = Table(title=title)
        table.add_column("Abbrev")
        table.add_column("Conference")
        table.add_column("Relevance", justify="right")
        table.add_column("Years")
        for row in rows:
            abbrev = row.get("abbreviation") or ""
            name = row.get("conference_name") or ""
            rel = row.get("conf_relevance")
            rel_str = f"{rel:.3f}" if isinstance(rel, (float, int)) else ""
            years = row.get("list_of_years") or []
            years_str = ", ".join(str(y) for y in years[:5])
            table.add_row(str(abbrev), str(name), rel_str, years_str)
        return _render(table)
    return format_table(data, title)


def _extract_collection_papers(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ("papers", "digest_df", "items", "results", "data"):
            val = data.get(key)
            if isinstance(val, list):
                return [item for item in val if isinstance(item, dict)]
        collections = data.get("collections")
        if isinstance(collections, list):
            papers: list[dict[str, Any]] = []
            for collection in collections:
                if isinstance(collection, dict):
                    for key in ("papers", "digest_df"):
                        val = collection.get(key)
                        if isinstance(val, list):
                            papers.extend([item for item in val if isinstance(item, dict)])
            if papers:
                return papers
    return []


def format_collection_papers(data: Any, title: str | None = None) -> str:
    papers = _extract_collection_papers(data)
    if papers:
        return format_table(papers, title)
    return format_table(data, title)
