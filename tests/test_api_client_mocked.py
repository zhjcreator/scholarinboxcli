from __future__ import annotations

from scholarinboxcli.api.client import ApiError, ScholarInboxClient


def test_bookmark_add_sends_expected_json_payload(monkeypatch):
    client = ScholarInboxClient()
    calls = []

    def fake_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return {"ok": True}

    monkeypatch.setattr(client, "_request", fake_request)
    try:
        out = client.bookmark_add("3302478")
    finally:
        client.close()

    assert out == {"ok": True}
    assert calls == [("POST", "/api/bookmark_paper/", {"json": {"bookmarked": True, "id": "3302478"}})]


def test_bookmark_remove_falls_back_to_form_payload(monkeypatch):
    client = ScholarInboxClient()
    calls = []

    def fake_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        if len(calls) == 1:
            raise ApiError("boom", 500, None)
        return {"ok": True}

    monkeypatch.setattr(client, "_request", fake_request)
    try:
        out = client.bookmark_remove("3302478")
    finally:
        client.close()

    assert out == {"ok": True}
    assert calls[0] == ("POST", "/api/bookmark_paper/", {"json": {"bookmarked": False, "id": "3302478"}})
    assert calls[1] == ("POST", "/api/bookmark_paper/", {"data": {"bookmarked": False, "id": "3302478"}})


def test_conference_explorer_uses_unfiltered_endpoint(monkeypatch):
    client = ScholarInboxClient()
    calls = []

    def fake_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return {"conf_data_list": []}

    monkeypatch.setattr(client, "_request", fake_request)
    try:
        out = client.conference_explorer()
    finally:
        client.close()

    assert out == {"conf_data_list": []}
    assert calls == [("GET", "/api/conference-explorer", {})]
