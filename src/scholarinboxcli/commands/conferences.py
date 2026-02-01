"""Conference command group."""

from __future__ import annotations

import typer

from scholarinboxcli.commands.common import print_output, with_client
from scholarinboxcli.formatters.domain_tables import format_conference_explore, format_conference_list


app = typer.Typer(help="Conference commands", no_args_is_help=True)


@app.command("list")
def conference_list(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    def action(client):
        data = client.conference_list()
        print_output(data, json_output, title="Conferences", table_formatter=format_conference_list)

    with_client(no_retry, action)


@app.command("explore")
def conference_explore(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    def action(client):
        data = client.conference_explorer()
        print_output(data, json_output, title="Conference Explorer", table_formatter=format_conference_explore)

    with_client(no_retry, action)
