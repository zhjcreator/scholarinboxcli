"""Authentication command group."""

from __future__ import annotations

import os

import typer

from scholarinboxcli.commands.common import print_output, with_client
from scholarinboxcli.formatters.domain_tables import format_auth_status


app = typer.Typer(help="Authentication commands", no_args_is_help=True)


@app.command("login")
def auth_login(
    url: str | None = typer.Option(None, "--url", help="Magic login URL with sha_key"),
    sha_key: str | None = typer.Option(
        None, "--sha-key", help="SHA key directly (requires SCHOLAR_INBOX_SHA_KEY env var or this flag)"
    ),
):
    if not url and not sha_key:
        # Fall back to SCHOLAR_INBOX_SHA_KEY env var
        sha_key = os.environ.get("SCHOLAR_INBOX_SHA_KEY")

    if not url and not sha_key:
        typer.echo("Provide --url, --sha-key, or set SCHOLAR_INBOX_SHA_KEY", err=True)
        raise typer.Exit(1)

    def action(client):
        if sha_key:
            client.login_with_magic_link(
                f"https://www.scholar-inbox.com/login?sha_key={sha_key}&date=01-01-2000"
            )
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
