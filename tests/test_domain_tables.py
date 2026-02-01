from __future__ import annotations

from scholarinboxcli.formatters.domain_tables import (
    format_auth_status,
    format_collection_list,
    format_conference_explore,
    format_conference_list,
)


def test_format_auth_status_table():
    out = format_auth_status({"is_logged_in": True, "name": "Marek"}, "Session")
    assert "is_logged_in" in out
    assert "Marek" in out


def test_format_collection_list_for_names():
    out = format_collection_list(["AIAgents", "Benchmark"], "Collections")
    assert "AIAgents" in out
    assert "Benchmark" in out


def test_format_conference_list_table():
    data = {
        "conferences": [
            {
                "conference_id": 1,
                "short_title": "ICLR 2026",
                "start_date": "2026-01-01",
                "end_date": "2026-01-05",
                "conference_url": "iclr/2026",
            }
        ]
    }
    out = format_conference_list(data, "Conferences")
    assert "ICLR 2026" in out
    assert "iclr/2026" in out


def test_format_conference_explore_table():
    data = {
        "conf_data_list": [
            {
                "abbreviation": "ACL",
                "conference_name": "Annual Meeting of ACL",
                "conf_relevance": 0.9,
                "list_of_years": [2025, 2024],
            }
        ]
    }
    out = format_conference_explore(data, "Conference Explorer")
    assert "ACL" in out
    assert "0.900" in out
