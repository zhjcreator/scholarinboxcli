from __future__ import annotations

from scholarinboxcli.formatters.table import format_table


def test_format_table_renders_key_value_dict():
    output = format_table({"is_logged_in": True, "name": "Test User"}, title="Session")
    assert "(no results)" not in output
    assert "is_logged_in" in output
    assert "Test User" in output


def test_format_table_renders_scalar_list():
    output = format_table(["AIAgents", "Benchmark"], title="Collections")
    assert "(no results)" not in output
    assert "AIAgents" in output
    assert "Benchmark" in output
