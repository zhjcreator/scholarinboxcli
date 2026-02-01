"""Bookmark command group."""

from __future__ import annotations

import typer

from scholarinboxcli.api.client import ApiError
from scholarinboxcli.commands.common import close_client, handle_error, print_output


app = typer.Typer(help="Bookmark commands", no_args_is_help=True)


@app.command("list")
def bookmark_list(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    from scholarinboxcli.commands.common import ScholarInboxClient

    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.bookmarks()
        print_output(data, json_output, title="Bookmarks")
    except ApiError as e:
        handle_error(e)
    finally:
        close_client(client)


@app.command("add")
def bookmark_add(
    paper_id: str = typer.Argument(..., help="Paper ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    from scholarinboxcli.commands.common import ScholarInboxClient

    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.bookmark_add(paper_id)
        print_output(data, json_output, title="Bookmark added")
    except ApiError as e:
        handle_error(e)
    finally:
        close_client(client)


@app.command("remove")
def bookmark_remove(
    paper_id: str = typer.Argument(..., help="Paper ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    from scholarinboxcli.commands.common import ScholarInboxClient

    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.bookmark_remove(paper_id)
        print_output(data, json_output, title="Bookmark removed")
    except ApiError as e:
        handle_error(e)
    finally:
        close_client(client)
