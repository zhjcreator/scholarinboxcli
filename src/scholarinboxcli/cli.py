"""Scholar Inbox CLI."""

from __future__ import annotations

import sys
from typing import Optional

import typer

from scholarinboxcli.api.client import ApiError, ScholarInboxClient
from scholarinboxcli.formatters.json_fmt import format_json
from scholarinboxcli.formatters.table import format_table

app = typer.Typer(
    help=(
        "Scholar Inbox CLI.\n\n"
        "Examples:\n"
        "  scholarinboxcli auth login --url \"https://www.scholar-inbox.com/login?sha_key=...&date=MM-DD-YYYY\"\n"
        "  scholarinboxcli digest --date 01-30-2026 --json\n"
        "  scholarinboxcli search \"transformers\" --limit 5 --json\n"
        "  scholarinboxcli collection papers \"AIAgents\" --json\n"
        "  scholarinboxcli conference explore --json\n"
    )
)


auth_app = typer.Typer(help="Authentication commands", no_args_is_help=True)
collection_app = typer.Typer(help="Collection commands", no_args_is_help=True)
bookmark_app = typer.Typer(help="Bookmark commands", no_args_is_help=True)
conference_app = typer.Typer(help="Conference commands", no_args_is_help=True)

app.add_typer(auth_app, name="auth")
app.add_typer(collection_app, name="collection")
app.add_typer(bookmark_app, name="bookmark")
app.add_typer(conference_app, name="conference")


def _print_output(data, use_json: bool, title: str | None = None) -> None:
    if use_json or not sys.stdout.isatty():
        typer.echo(format_json(data))
        return
    table = format_table(data, title=title)
    if table == "(no results)":
        typer.echo(table)
        return
    typer.echo(table)


def _handle_error(err: ApiError) -> None:
    if not sys.stdout.isatty():
        typer.echo(format_json({"error": err.message, "status_code": err.status_code, "detail": err.detail}))
    else:
        typer.echo(f"Error: {err.message}", err=True)
        if err.status_code:
            typer.echo(f"Status: {err.status_code}", err=True)
    raise typer.Exit(1)


def _normalize_name(name: str) -> str:
    return name.strip().lower()


def _resolve_collection_id(client: ScholarInboxClient, identifier: str) -> str:
    if identifier.isdigit():
        return identifier
    data = client.collections_list()
    items = _collection_items_from_response(data)
    candidates = _collection_candidates(items)
    if not _candidates_have_ids(candidates):
        try:
            data = client.collections_expanded()
            items = _collection_items_from_response(data)
            candidates = _collection_candidates(items)
        except ApiError:
            pass
    if not _candidates_have_ids(candidates):
        try:
            data = client.collections_map()
            mapped = _collection_candidates_from_map(data)
            if mapped:
                candidates = mapped
        except ApiError:
            pass
    if not _candidates_have_ids(candidates):
        matched = _match_collection_name(candidates, identifier)
        if matched:
            # Only names are available; fall back to name as identifier.
            return matched
        raise ApiError("Unable to resolve collection name (no IDs available)")
    candidates = [(name, cid) for name, cid in candidates if cid]
    target = _normalize_name(identifier)
    for name, cid in candidates:
        if _normalize_name(name) == target:
            return cid
    # prefix match
    prefix = [c for c in candidates if _normalize_name(c[0]).startswith(target)]
    if len(prefix) == 1:
        return prefix[0][1]
    if len(prefix) > 1:
        names = ", ".join([f"{n}({cid})" for n, cid in prefix[:10]])
        raise ApiError(f"Ambiguous collection name. Matches: {names}")
    # contains match
    contains = [c for c in candidates if target in _normalize_name(c[0])]
    if len(contains) == 1:
        return contains[0][1]
    if len(contains) > 1:
        names = ", ".join([f"{n}({cid})" for n, cid in contains[:10]])
        raise ApiError(f"Ambiguous collection name. Matches: {names}")
    raise ApiError("Collection name not found")


def _collection_candidates(items: object) -> list[tuple[str, str]]:
    if not isinstance(items, list):
        return []
    candidates: list[tuple[str, str]] = []
    for item in items:
        if isinstance(item, dict):
            name = item.get("name") or item.get("collection_name") or ""
            cid = str(item.get("id") or item.get("collection_id") or "")
        elif isinstance(item, str):
            name = item
            cid = ""
        else:
            continue
        if name:
            candidates.append((name, cid))
    return candidates


def _collection_items_from_response(data: object) -> object:
    if isinstance(data, dict):
        for key in ("collections", "expanded_collections", "collection_names"):
            if key in data:
                return data.get(key)
        return data
    return data


def _collection_candidates_from_map(data: object) -> list[tuple[str, str]]:
    if not isinstance(data, dict):
        return []
    mapping = data.get("collection_names_to_ids_dict")
    if not isinstance(mapping, dict):
        return []
    candidates: list[tuple[str, str]] = []
    for name, cid in mapping.items():
        if name and cid is not None:
            candidates.append((str(name), str(cid)))
    return candidates


def _candidates_have_ids(candidates: list[tuple[str, str]]) -> bool:
    for _, cid in candidates:
        if cid:
            return True
    return False


def _match_collection_name(candidates: list[tuple[str, str]], identifier: str) -> str | None:
    target = _normalize_name(identifier)
    names = [(name, cid) for name, cid in candidates if name]
    for name, _ in names:
        if _normalize_name(name) == target:
            return name
    prefix = [c for c in names if _normalize_name(c[0]).startswith(target)]
    if len(prefix) == 1:
        return prefix[0][0]
    if len(prefix) > 1:
        names_str = ", ".join([n for n, _ in prefix[:10]])
        raise ApiError(f"Ambiguous collection name. Matches: {names_str}")
    contains = [c for c in names if target in _normalize_name(c[0])]
    if len(contains) == 1:
        return contains[0][0]
    if len(contains) > 1:
        names_str = ", ".join([n for n, _ in contains[:10]])
        raise ApiError(f"Ambiguous collection name. Matches: {names_str}")
    return None


@auth_app.command("login")
def auth_login(
    url: str = typer.Option(..., "--url", help="Magic login URL with sha_key"),
):
    client = ScholarInboxClient()
    try:
        client.login_with_magic_link(url)
        typer.echo("Login successful")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@auth_app.command("status")
def auth_status(json_output: bool = typer.Option(False, "--json", help="Output as JSON")):
    client = ScholarInboxClient()
    try:
        data = client.session_info()
        _print_output(data, json_output, title="Session")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@auth_app.command("logout")
def auth_logout():
    from scholarinboxcli.config import save_config, Config

    save_config(Config())
    typer.echo("Logged out")


@app.command("digest")
def digest(
    date: Optional[str] = typer.Option(None, "--date", help="Digest date (MM-DD-YYYY)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.get_digest(date)
        _print_output(data, json_output, title="Digest")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@app.command("trending")
def trending(
    category: str = typer.Option("ALL", "--category", help="Category filter"),
    days: int = typer.Option(7, "--days", help="Lookback window in days"),
    sort: str = typer.Option("hype", "--sort", help="Sort column"),
    asc: bool = typer.Option(False, "--asc", help="Sort ascending"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.get_trending(category=category, days=days, sort=sort, asc=asc)
        _print_output(data, json_output, title="Trending")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@app.command("search")
def search(
    query: str = typer.Argument(..., help="Search query"),
    sort: Optional[str] = typer.Option(None, "--sort", help="Sort option"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit results"),
    offset: Optional[int] = typer.Option(None, "--offset", help="Pagination offset"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.search(query=query, sort=sort, limit=limit, offset=offset)
        _print_output(data, json_output, title="Search")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@app.command("semantic")
def semantic_search(
    text: Optional[str] = typer.Argument(None, help="Semantic search text"),
    file: Optional[str] = typer.Option(None, "--file", help="Read query text from file"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit results"),
    offset: Optional[int] = typer.Option(None, "--offset", help="Pagination offset"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    if not text and not file:
        typer.echo("Provide text or --file", err=True)
        raise typer.Exit(1)
    if file:
        text = open(file, "r", encoding="utf-8").read()
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.semantic_search(text=text or "", limit=limit, offset=offset)
        _print_output(data, json_output, title="Semantic Search")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@app.command("interactions")
def interactions(
    type_: str = typer.Option("all", "--type", help="Interaction type (all/up/down)"),
    sort: str = typer.Option("ranking_score", "--sort", help="Sort column"),
    asc: bool = typer.Option(False, "--asc", help="Sort ascending"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.interactions(type_=type_, sort=sort, asc=asc)
        _print_output(data, json_output, title="Interactions")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@bookmark_app.command("list")
def bookmark_list(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.bookmarks()
        _print_output(data, json_output, title="Bookmarks")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@bookmark_app.command("add")
def bookmark_add(
    paper_id: str = typer.Argument(..., help="Paper ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.bookmark_add(paper_id)
        _print_output(data, json_output, title="Bookmark added")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@bookmark_app.command("remove")
def bookmark_remove(
    paper_id: str = typer.Argument(..., help="Paper ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.bookmark_remove(paper_id)
        _print_output(data, json_output, title="Bookmark removed")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@collection_app.command("list")
def collection_list(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    expanded: bool = typer.Option(False, "--expanded", help="Use expanded collection metadata"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.collections_expanded() if expanded else client.collections_list()
        _print_output(data, json_output, title="Collections")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()

@collection_app.command("create")
def collection_create(
    name: str = typer.Argument(..., help="Collection name"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.collection_create(name)
        _print_output(data, json_output, title="Collection created")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@collection_app.command("rename")
def collection_rename(
    collection_id: str = typer.Argument(..., help="Collection ID or name"),
    new_name: str = typer.Argument(..., help="New collection name"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        cid = _resolve_collection_id(client, collection_id)
        data = client.collection_rename(cid, new_name)
        _print_output(data, json_output, title="Collection renamed")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@collection_app.command("delete")
def collection_delete(
    collection_id: str = typer.Argument(..., help="Collection ID or name"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        cid = _resolve_collection_id(client, collection_id)
        data = client.collection_delete(cid)
        _print_output(data, json_output, title="Collection deleted")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@collection_app.command("add")
def collection_add(
    collection_id: str = typer.Argument(..., help="Collection ID or name"),
    paper_id: str = typer.Argument(..., help="Paper ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        cid = _resolve_collection_id(client, collection_id)
        data = client.collection_add_paper(cid, paper_id)
        _print_output(data, json_output, title="Collection add paper")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@collection_app.command("remove")
def collection_remove(
    collection_id: str = typer.Argument(..., help="Collection ID or name"),
    paper_id: str = typer.Argument(..., help="Paper ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        cid = _resolve_collection_id(client, collection_id)
        data = client.collection_remove_paper(cid, paper_id)
        _print_output(data, json_output, title="Collection remove paper")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@collection_app.command("papers")
def collection_papers(
    collection_id: str = typer.Argument(..., help="Collection ID or name"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit results"),
    offset: Optional[int] = typer.Option(None, "--offset", help="Pagination offset"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        cid = _resolve_collection_id(client, collection_id)
        data = client.collection_papers(cid, limit=limit, offset=offset)
        _print_output(data, json_output, title=f"Collection {cid}")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@collection_app.command("similar")
def collection_similar(
    collection_ids: list[str] = typer.Argument(..., help="Collection ID(s) or names"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit results"),
    offset: Optional[int] = typer.Option(None, "--offset", help="Pagination offset"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        resolved = [_resolve_collection_id(client, cid) for cid in collection_ids]
        data = client.collections_similar(resolved, limit=limit, offset=offset)
        _print_output(data, json_output, title="Similar Papers")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@conference_app.command("list")
def conference_list(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.conference_list()
        _print_output(data, json_output, title="Conferences")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@conference_app.command("explore")
def conference_explore(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.conference_explorer()
        _print_output(data, json_output, title="Conference Explorer")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()
