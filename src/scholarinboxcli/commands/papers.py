"""Top-level feed/search related commands."""

from __future__ import annotations

from typing import Optional

import typer

from scholarinboxcli.api.client import ApiError
from scholarinboxcli.commands.common import close_client, handle_error, print_output


def register(app: typer.Typer) -> None:
    @app.command("digest")
    def digest(
        date: Optional[str] = typer.Option(None, "--date", help="Digest date (MM-DD-YYYY)"),
        json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
        no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
    ):
        from scholarinboxcli.commands.common import ScholarInboxClient

        client = ScholarInboxClient(no_retry=no_retry)
        try:
            data = client.get_digest(date)
            print_output(data, json_output, title="Digest")
        except ApiError as e:
            handle_error(e)
        finally:
            close_client(client)

    @app.command("trending")
    def trending(
        category: str = typer.Option("ALL", "--category", help="Category filter"),
        days: int = typer.Option(7, "--days", help="Lookback window in days"),
        sort: str = typer.Option("hype", "--sort", help="Sort column"),
        asc: bool = typer.Option(False, "--asc", help="Sort ascending"),
        json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
        no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
    ):
        from scholarinboxcli.commands.common import ScholarInboxClient

        client = ScholarInboxClient(no_retry=no_retry)
        try:
            data = client.get_trending(category=category, days=days, sort=sort, asc=asc)
            print_output(data, json_output, title="Trending")
        except ApiError as e:
            handle_error(e)
        finally:
            close_client(client)

    @app.command("search")
    def search(
        query: str = typer.Argument(..., help="Search query"),
        sort: Optional[str] = typer.Option(None, "--sort", help="Sort option"),
        limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit results"),
        offset: Optional[int] = typer.Option(None, "--offset", help="Pagination offset"),
        json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
        no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
    ):
        from scholarinboxcli.commands.common import ScholarInboxClient

        client = ScholarInboxClient(no_retry=no_retry)
        try:
            data = client.search(query=query, sort=sort, limit=limit, offset=offset)
            print_output(data, json_output, title="Search")
        except ApiError as e:
            handle_error(e)
        finally:
            close_client(client)

    @app.command("semantic")
    def semantic_search(
        text: Optional[str] = typer.Argument(None, help="Semantic search text"),
        file: Optional[str] = typer.Option(None, "--file", help="Read query text from file"),
        limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit results"),
        offset: Optional[int] = typer.Option(None, "--offset", help="Pagination offset"),
        json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
        no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
    ):
        from scholarinboxcli.commands.common import ScholarInboxClient

        if not text and not file:
            typer.echo("Provide text or --file", err=True)
            raise typer.Exit(1)
        if file:
            text = open(file, "r", encoding="utf-8").read()

        client = ScholarInboxClient(no_retry=no_retry)
        try:
            data = client.semantic_search(text=text or "", limit=limit, offset=offset)
            print_output(data, json_output, title="Semantic Search")
        except ApiError as e:
            handle_error(e)
        finally:
            close_client(client)

    @app.command("interactions")
    def interactions(
        type_: str = typer.Option("all", "--type", help="Interaction type (all/up/down)"),
        sort: str = typer.Option("ranking_score", "--sort", help="Sort column"),
        asc: bool = typer.Option(False, "--asc", help="Sort ascending"),
        json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
        no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
    ):
        from scholarinboxcli.commands.common import ScholarInboxClient

        client = ScholarInboxClient(no_retry=no_retry)
        try:
            data = client.interactions(type_=type_, sort=sort, asc=asc)
            print_output(data, json_output, title="Interactions")
        except ApiError as e:
            handle_error(e)
        finally:
            close_client(client)
