"""Conference command group."""

from __future__ import annotations

import typer

from scholarinboxcli.api.client import ApiError
from scholarinboxcli.commands.common import close_client, handle_error, print_output


app = typer.Typer(help="Conference commands", no_args_is_help=True)


@app.command("list")
def conference_list(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    from scholarinboxcli.commands.common import ScholarInboxClient

    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.conference_list()
        print_output(data, json_output, title="Conferences")
    except ApiError as e:
        handle_error(e)
    finally:
        close_client(client)


@app.command("explore")
def conference_explore(
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    no_retry: bool = typer.Option(False, "--no-retry", help="Disable retry on rate limits"),
):
    from scholarinboxcli.commands.common import ScholarInboxClient

    client = ScholarInboxClient(no_retry=no_retry)
    try:
        data = client.conference_explorer()
        print_output(data, json_output, title="Conference Explorer")
    except ApiError as e:
        handle_error(e)
    finally:
        close_client(client)
