from __future__ import annotations

import pytest

from scholarinboxcli.api.client import ApiError
from scholarinboxcli import cli


class _FakeClient:
    def __init__(self, collections=None, expanded=None, mapping=None):
        self._collections = collections if collections is not None else []
        self._expanded = expanded if expanded is not None else {"expanded_collections": []}
        self._mapping = mapping if mapping is not None else {"collection_names_to_ids_dict": {}}

    def collections_list(self):
        return self._collections

    def collections_expanded(self):
        return self._expanded

    def collections_map(self):
        return self._mapping


def test_resolve_collection_id_returns_numeric_input_as_is():
    client = _FakeClient()
    assert cli._resolve_collection_id(client, "12345") == "12345"


def test_resolve_collection_id_exact_name_match():
    client = _FakeClient(
        collections=[
            {"name": "AIAgents", "id": 100},
            {"name": "Benchmark", "id": 200},
        ]
    )
    assert cli._resolve_collection_id(client, "AIAgents") == "100"


def test_resolve_collection_id_prefix_match():
    client = _FakeClient(
        collections=[
            {"name": "AIAgents", "id": 100},
            {"name": "Benchmark", "id": 200},
        ]
    )
    assert cli._resolve_collection_id(client, "AIA") == "100"


def test_resolve_collection_id_contains_match():
    client = _FakeClient(
        collections=[
            {"name": "AIAgents", "id": 100},
            {"name": "Benchmark", "id": 200},
        ]
    )
    assert cli._resolve_collection_id(client, "gent") == "100"


def test_resolve_collection_id_ambiguous_prefix_raises():
    client = _FakeClient(
        collections=[
            {"name": "AgentBench", "id": 10},
            {"name": "AgentEval", "id": 20},
        ]
    )
    with pytest.raises(ApiError, match="Ambiguous collection name"):
        cli._resolve_collection_id(client, "Agent")


def test_resolve_collection_id_falls_back_to_mapping_when_ids_missing():
    client = _FakeClient(
        collections=["AIAgents", "Benchmark"],
        expanded={"expanded_collections": ["AIAgents"]},
        mapping={"collection_names_to_ids_dict": {"AIAgents": 4242, "Benchmark": 7}},
    )
    assert cli._resolve_collection_id(client, "AIAgents") == "4242"


def test_resolve_collection_id_not_found_raises():
    client = _FakeClient(
        collections=[{"name": "AIAgents", "id": 100}],
    )
    with pytest.raises(ApiError, match="Collection name not found"):
        cli._resolve_collection_id(client, "does-not-exist")
