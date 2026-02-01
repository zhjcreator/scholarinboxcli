from __future__ import annotations

from scholarinboxcli.services.paper_sort import sort_paper_response


def test_sort_paper_response_by_year_desc():
    data = {
        "digest_df": [
            {"title": "Old", "publication_date": "2020-01-01"},
            {"title": "New", "conference_year": 2024.0},
            {"title": "Mid", "year": 2022},
        ]
    }
    out = sort_paper_response(data, "year", asc=False)
    assert [p["title"] for p in out["digest_df"]] == ["New", "Mid", "Old"]


def test_sort_paper_response_by_title_asc():
    data = {
        "digest_df": [
            {"title": "zeta"},
            {"title": "Alpha"},
            {"title": "beta"},
        ]
    }
    out = sort_paper_response(data, "title", asc=True)
    assert [p["title"] for p in out["digest_df"]] == ["Alpha", "beta", "zeta"]
