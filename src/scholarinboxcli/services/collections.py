"""Collection name/ID resolution helpers."""

from __future__ import annotations

from typing import Any

from scholarinboxcli.api.client import ApiError, ScholarInboxClient


def normalize_name(name: str) -> str:
    return name.strip().lower()


def collection_candidates(items: object) -> list[tuple[str, str]]:
    if not isinstance(items, list):
        return []
    candidates: list[tuple[str, str]] = []
    for item in items:
        if isinstance(item, dict):
            name = item.get("name") or item.get("collection_name") or ""
            cid = str(item.get("id") or item.get("collection_id") or "")
        elif isinstance(item, str):
            name = item
            cid = ""
        else:
            continue
        if name:
            candidates.append((name, cid))
    return candidates


def collection_items_from_response(data: object) -> object:
    if isinstance(data, dict):
        for key in ("collections", "expanded_collections", "collection_names"):
            if key in data:
                return data.get(key)
        return data
    return data


def collection_candidates_from_map(data: object) -> list[tuple[str, str]]:
    if not isinstance(data, dict):
        return []
    mapping = data.get("collection_names_to_ids_dict")
    if not isinstance(mapping, dict):
        return []
    return [(str(name), str(cid)) for name, cid in mapping.items() if name and cid is not None]


def candidates_have_ids(candidates: list[tuple[str, str]]) -> bool:
    return any(cid for _, cid in candidates)


def match_collection_name(candidates: list[tuple[str, str]], identifier: str) -> str | None:
    target = normalize_name(identifier)
    names = [(name, cid) for name, cid in candidates if name]

    for name, _ in names:
        if normalize_name(name) == target:
            return name

    prefix = [c for c in names if normalize_name(c[0]).startswith(target)]
    if len(prefix) == 1:
        return prefix[0][0]
    if len(prefix) > 1:
        names_str = ", ".join([n for n, _ in prefix[:10]])
        raise ApiError(f"Ambiguous collection name. Matches: {names_str}")

    contains = [c for c in names if target in normalize_name(c[0])]
    if len(contains) == 1:
        return contains[0][0]
    if len(contains) > 1:
        names_str = ", ".join([n for n, _ in contains[:10]])
        raise ApiError(f"Ambiguous collection name. Matches: {names_str}")

    return None


def resolve_collection_id(client: ScholarInboxClient, identifier: str) -> str:
    """Resolve numeric IDs directly, otherwise match by collection name."""
    if identifier.isdigit():
        return identifier

    data = client.collections_list()
    items = collection_items_from_response(data)
    candidates = collection_candidates(items)

    if not candidates_have_ids(candidates):
        try:
            data = client.collections_expanded()
            items = collection_items_from_response(data)
            candidates = collection_candidates(items)
        except ApiError:
            pass

    if not candidates_have_ids(candidates):
        try:
            data = client.collections_map()
            mapped = collection_candidates_from_map(data)
            if mapped:
                candidates = mapped
        except ApiError:
            pass

    if not candidates_have_ids(candidates):
        matched = match_collection_name(candidates, identifier)
        if matched:
            return matched
        raise ApiError("Unable to resolve collection name (no IDs available)")

    candidates = [(name, cid) for name, cid in candidates if cid]
    target = normalize_name(identifier)

    for name, cid in candidates:
        if normalize_name(name) == target:
            return cid

    prefix = [c for c in candidates if normalize_name(c[0]).startswith(target)]
    if len(prefix) == 1:
        return prefix[0][1]
    if len(prefix) > 1:
        names = ", ".join([f"{n}({cid})" for n, cid in prefix[:10]])
        raise ApiError(f"Ambiguous collection name. Matches: {names}")

    contains = [c for c in candidates if target in normalize_name(c[0])]
    if len(contains) == 1:
        return contains[0][1]
    if len(contains) > 1:
        names = ", ".join([f"{n}({cid})" for n, cid in contains[:10]])
        raise ApiError(f"Ambiguous collection name. Matches: {names}")

    raise ApiError("Collection name not found")
