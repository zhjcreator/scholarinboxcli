"""Bookmark command group."""

from __future__ import annotations

import typer

from scholarinboxcli.commands.common import print_output, with_client
from scholarinboxcli.formatters.domain_tables import format_collection_papers


app = typer.Typer(help="Bookmark commands", no_args_is_help=True)


@app.command("list")
def bookmark_list(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    def action(client):
        data = client.bookmarks()
        print_output(data, json_output, title="Bookmarks", table_formatter=format_collection_papers)

    with_client(no_retry, action)


@app.command("add")
def bookmark_add(
    paper_id: str = typer.Argument(..., help="Paper ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    def action(client):
        data = client.bookmark_add(paper_id)
        print_output(data, json_output, title="Bookmark added")

    with_client(no_retry, action)


@app.command("remove")
def bookmark_remove(
    paper_id: str = typer.Argument(..., help="Paper ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    def action(client):
        data = client.bookmark_remove(paper_id)
        print_output(data, json_output, title="Bookmark removed")

    with_client(no_retry, action)
