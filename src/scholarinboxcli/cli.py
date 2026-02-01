"""Scholar Inbox CLI."""

from __future__ import annotations

import sys
from typing import Optional

import typer

from scholarinboxcli.api.client import ApiError, ScholarInboxClient
from scholarinboxcli.formatters.json_fmt import format_json
from scholarinboxcli.formatters.table import format_table

app = typer.Typer(help="Scholar Inbox CLI")


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
    collection_id: str = typer.Argument(..., help="Collection ID"),
    new_name: str = typer.Argument(..., help="New collection name"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.collection_rename(collection_id, new_name)
        _print_output(data, json_output, title="Collection renamed")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@collection_app.command("delete")
def collection_delete(
    collection_id: str = typer.Argument(..., help="Collection ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.collection_delete(collection_id)
        _print_output(data, json_output, title="Collection deleted")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@collection_app.command("add")
def collection_add(
    collection_id: str = typer.Argument(..., help="Collection ID"),
    paper_id: str = typer.Argument(..., help="Paper ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.collection_add_paper(collection_id, paper_id)
        _print_output(data, json_output, title="Collection add paper")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@collection_app.command("remove")
def collection_remove(
    collection_id: str = typer.Argument(..., help="Collection ID"),
    paper_id: str = typer.Argument(..., help="Paper ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.collection_remove_paper(collection_id, paper_id)
        _print_output(data, json_output, title="Collection remove paper")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@collection_app.command("papers")
def collection_papers(
    collection_id: str = typer.Argument(..., help="Collection ID"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit results"),
    offset: Optional[int] = typer.Option(None, "--offset", help="Pagination offset"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.collection_papers(collection_id, limit=limit, offset=offset)
        _print_output(data, json_output, title=f"Collection {collection_id}")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()


@collection_app.command("similar")
def collection_similar(
    collection_ids: list[str] = typer.Argument(..., help="Collection ID(s)"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit results"),
    offset: Optional[int] = typer.Option(None, "--offset", help="Pagination offset"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.collections_similar(collection_ids, limit=limit, offset=offset)
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
    query: Optional[str] = typer.Option(None, "--query", help="Search query"),
    sort: Optional[str] = typer.Option(None, "--sort", help="Sort option"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.conference_explorer(query=query, sort=sort)
        _print_output(data, json_output, title="Conference Explorer")
    except ApiError as e:
        _handle_error(e)
    finally:
        client.close()
