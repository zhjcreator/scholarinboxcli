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


def test_format_table_extracts_year_from_publication_date():
    data = {
        "digest_df": [
            {
                "title": "Paper",
                "authors": "A, B",
                "publication_date": "2025-12-01",
                "paper_id": 1,
            }
        ]
    }
    output = format_table(data, title="Papers")
    assert "2025" in output


def test_format_table_truncates_long_authors():
    long_authors = ", ".join([f"Author{i}" for i in range(1, 30)])
    data = {
        "digest_df": [
            {
                "title": "Paper",
                "authors": long_authors,
                "year": 2025,
                "paper_id": 1,
            }
        ]
    }
    output = format_table(data, title="Papers")
    assert "..." in output
