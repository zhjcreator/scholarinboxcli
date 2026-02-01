from __future__ import annotations

from typer.testing import CliRunner

import scholarinboxcli.cli as cli


class _FakeClient:
    def __init__(self, no_retry: bool = False):  # noqa: ARG002
        pass

    def session_info(self):
        return {"is_logged_in": True, "name": "Test User"}

    def conference_explorer(self):
        return {"conf_data_list": [{"abbreviation": "ACL"}]}

    def close(self):
        return None


def test_auth_status_json_is_pretty(monkeypatch):
    runner = CliRunner()
    monkeypatch.setattr(cli, "ScholarInboxClient", _FakeClient)

    result = runner.invoke(cli.app, ["auth", "status", "--json"])

    assert result.exit_code == 0
    assert '{\n  "is_logged_in": true,' in result.stdout


def test_conference_explore_json(monkeypatch):
    runner = CliRunner()
    monkeypatch.setattr(cli, "ScholarInboxClient", _FakeClient)

    result = runner.invoke(cli.app, ["conference", "explore", "--json"])

    assert result.exit_code == 0
    assert '"conf_data_list"' in result.stdout
    assert '"ACL"' in result.stdout


def test_conference_explore_query_option_removed():
    runner = CliRunner()

    result = runner.invoke(cli.app, ["conference", "explore", "--query", "nlp"])
    combined = result.stdout + (result.stderr or "")

    assert result.exit_code != 0
    assert "No such option: --query" in combined
