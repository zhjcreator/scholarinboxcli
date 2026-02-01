"""Collection command group."""

from __future__ import annotations

from typing import Optional

import typer

from scholarinboxcli.api.client import ApiError
from scholarinboxcli.commands.common import close_client, handle_error, print_output
from scholarinboxcli.services.collections import resolve_collection_id


app = typer.Typer(help="Collection commands", no_args_is_help=True)


@app.command("list")
def collection_list(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    expanded: bool = typer.Option(False, "--expanded", help="Use expanded collection metadata"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    from scholarinboxcli.commands.common import ScholarInboxClient

    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.collections_expanded() if expanded else client.collections_list()
        print_output(data, json_output, title="Collections")
    except ApiError as e:
        handle_error(e)
    finally:
        close_client(client)


@app.command("create")
def collection_create(
    name: str = typer.Argument(..., help="Collection name"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    from scholarinboxcli.commands.common import ScholarInboxClient

    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.collection_create(name)
        print_output(data, json_output, title="Collection created")
    except ApiError as e:
        handle_error(e)
    finally:
        close_client(client)


@app.command("rename")
def collection_rename(
    collection_id: str = typer.Argument(..., help="Collection ID or name"),
    new_name: str = typer.Argument(..., help="New collection name"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    from scholarinboxcli.commands.common import ScholarInboxClient

    client = ScholarInboxClient(no_retry=no_retry)
    try:
        cid = resolve_collection_id(client, collection_id)
        data = client.collection_rename(cid, new_name)
        print_output(data, json_output, title="Collection renamed")
    except ApiError as e:
        handle_error(e)
    finally:
        close_client(client)


@app.command("delete")
def collection_delete(
    collection_id: str = typer.Argument(..., help="Collection ID or name"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    from scholarinboxcli.commands.common import ScholarInboxClient

    client = ScholarInboxClient(no_retry=no_retry)
    try:
        cid = resolve_collection_id(client, collection_id)
        data = client.collection_delete(cid)
        print_output(data, json_output, title="Collection deleted")
    except ApiError as e:
        handle_error(e)
    finally:
        close_client(client)


@app.command("add")
def collection_add(
    collection_id: str = typer.Argument(..., help="Collection ID or name"),
    paper_id: str = typer.Argument(..., help="Paper ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    from scholarinboxcli.commands.common import ScholarInboxClient

    client = ScholarInboxClient(no_retry=no_retry)
    try:
        cid = resolve_collection_id(client, collection_id)
        data = client.collection_add_paper(cid, paper_id)
        print_output(data, json_output, title="Collection add paper")
    except ApiError as e:
        handle_error(e)
    finally:
        close_client(client)


@app.command("remove")
def collection_remove(
    collection_id: str = typer.Argument(..., help="Collection ID or name"),
    paper_id: str = typer.Argument(..., help="Paper ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    from scholarinboxcli.commands.common import ScholarInboxClient

    client = ScholarInboxClient(no_retry=no_retry)
    try:
        cid = resolve_collection_id(client, collection_id)
        data = client.collection_remove_paper(cid, paper_id)
        print_output(data, json_output, title="Collection remove paper")
    except ApiError as e:
        handle_error(e)
    finally:
        close_client(client)


@app.command("papers")
def collection_papers(
    collection_id: str = typer.Argument(..., help="Collection ID or name"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit results"),
    offset: Optional[int] = typer.Option(None, "--offset", help="Pagination offset"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    from scholarinboxcli.commands.common import ScholarInboxClient

    client = ScholarInboxClient(no_retry=no_retry)
    try:
        cid = resolve_collection_id(client, collection_id)
        data = client.collection_papers(cid, limit=limit, offset=offset)
        print_output(data, json_output, title=f"Collection {cid}")
    except ApiError as e:
        handle_error(e)
    finally:
        close_client(client)


@app.command("similar")
def collection_similar(
    collection_ids: list[str] = typer.Argument(..., help="Collection ID(s) or names"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit results"),
    offset: Optional[int] = typer.Option(None, "--offset", help="Pagination offset"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    from scholarinboxcli.commands.common import ScholarInboxClient

    client = ScholarInboxClient(no_retry=no_retry)
    try:
        resolved = [resolve_collection_id(client, cid) for cid in collection_ids]
        data = client.collections_similar(resolved, limit=limit, offset=offset)
        print_output(data, json_output, title="Similar Papers")
    except ApiError as e:
        handle_error(e)
    finally:
        close_client(client)
