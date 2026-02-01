"""Authentication command group."""

from __future__ import annotations

import typer

from scholarinboxcli.commands.common import print_output, with_client


app = typer.Typer(help="Authentication commands", no_args_is_help=True)


@app.command("login")
def auth_login(
    url: str = typer.Option(..., "--url", help="Magic login URL with sha_key"),
):
    def action(client):
        client.login_with_magic_link(url)
        typer.echo("Login successful")

    with_client(False, action)


@app.command("status")
def auth_status(json_output: bool = typer.Option(False, "--json", help="Output as JSON")):
    def action(client):
        data = client.session_info()
        print_output(data, json_output, title="Session")

    with_client(False, action)


@app.command("logout")
def auth_logout():
    from scholarinboxcli.config import Config, save_config

    save_config(Config())
    typer.echo("Logged out")
