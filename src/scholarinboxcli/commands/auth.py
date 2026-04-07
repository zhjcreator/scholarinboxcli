"""Authentication command group."""

from __future__ import annotations

from typing import Optional

import typer

from scholarinboxcli.commands.common import print_output, with_client
from scholarinboxcli.formatters.domain_tables import format_auth_status


app = typer.Typer(help="Authentication commands", no_args_is_help=True)


@app.command("login")
def auth_login(
    url: Optional[str] = typer.Option(None, "--url", help="Magic login URL with sha_key"),
    sha_key: Optional[str] = typer.Option(None, "--sha-key", help="SHA key directly (without full URL)"),
):
    if not url and not sha_key:
        typer.echo("Provide --url or --sha-key", err=True)
        raise typer.Exit(1)

    def action(client):
        if sha_key:
            client.login_with_sha_key(sha_key)
        else:
            client.login_with_magic_link(url)
        typer.echo("Login successful")

    with_client(False, action)


@app.command("status")
def auth_status(json_output: bool = typer.Option(False, "--json", help="Output as JSON")):
    def action(client):
        data = client.session_info()
        print_output(data, json_output, title="Session", table_formatter=format_auth_status)

    with_client(False, action)


@app.command("logout")
def auth_logout():
    from scholarinboxcli.config import Config, save_config

    save_config(Config())
    typer.echo("Logged out")
