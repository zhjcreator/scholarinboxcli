"""Authentication command group."""

from __future__ import annotations

import typer

from scholarinboxcli.api.client import ApiError
from scholarinboxcli.commands.common import close_client, handle_error, print_output


app = typer.Typer(help="Authentication commands", no_args_is_help=True)


@app.command("login")
def auth_login(
    url: str = typer.Option(..., "--url", help="Magic login URL with sha_key"),
):
    from scholarinboxcli.commands.common import ScholarInboxClient

    client = ScholarInboxClient()
    try:
        client.login_with_magic_link(url)
        typer.echo("Login successful")
    except ApiError as e:
        handle_error(e)
    finally:
        close_client(client)


@app.command("status")
def auth_status(json_output: bool = typer.Option(False, "--json", help="Output as JSON")):
    from scholarinboxcli.commands.common import ScholarInboxClient

    client = ScholarInboxClient()
    try:
        data = client.session_info()
        print_output(data, json_output, title="Session")
    except ApiError as e:
        handle_error(e)
    finally:
        close_client(client)


@app.command("logout")
def auth_logout():
    from scholarinboxcli.config import Config, save_config

    save_config(Config())
    typer.echo("Logged out")
