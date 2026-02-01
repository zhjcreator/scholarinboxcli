"""HTTP client for Scholar Inbox web API."""

from __future__ import annotations

import json
import os
import time
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass
from http.cookiejar import Cookie
from typing import Any

import httpx

from scholarinboxcli.config import Config, load_config, save_config


@dataclass
class ApiError(Exception):
    message: str
    status_code: int | None = None
    detail: Any | None = None


def _cookie_to_dict(cookie: Cookie) -> dict[str, Any]:
    return {
        "name": cookie.name,
        "value": cookie.value,
        "domain": cookie.domain,
        "path": cookie.path,
        "expires": cookie.expires,
        "secure": cookie.secure,
        "httponly": cookie.has_nonstandard_attr("HttpOnly"),
    }


def _cookies_to_list(cookies: httpx.Cookies) -> list[dict[str, Any]]:
    return [_cookie_to_dict(c) for c in cookies.jar]


def _cookies_from_list(items: list[dict[str, Any]] | None) -> httpx.Cookies:
    jar = httpx.Cookies()
    if not items:
        return jar
    for item in items:
        jar.set(
            item.get("name"),
            item.get("value"),
            domain=item.get("domain"),
            path=item.get("path") or "/",
        )
    return jar


def _normalize_cookie_domains(cookies: httpx.Cookies, api_base: str) -> httpx.Cookies:
    host = api_base.replace("https://", "").replace("http://", "").split("/")[0]
    extra: list[tuple[str, str, str]] = []
    for c in cookies.jar:
        domain = c.domain or ""
        if domain.startswith("www."):
            base = domain[len("www.") :]
        else:
            base = domain
        if base and host.endswith(base) and domain != host:
            extra.append((c.name, c.value, host))
        if base and not base.startswith("."):
            extra.append((c.name, c.value, f".{base}"))
    for name, value, domain in extra:
        cookies.set(name, value, domain=domain, path="/")
    return cookies


def _is_paper_list(data: Any) -> bool:
    if isinstance(data, dict):
        for key in ("papers", "results", "items", "data", "digest_df"):
            val = data.get(key)
            if isinstance(val, list):
                return True
    if isinstance(data, list):
        return True
    return False


class ScholarInboxClient:
    def __init__(self, api_base: str | None = None, no_retry: bool = False):
        self.no_retry = no_retry
        self.cfg = load_config()
        self.api_base = api_base or os.environ.get("SCHOLAR_INBOX_API_BASE") or self.cfg.api_base
        cookies = _cookies_from_list(self.cfg.cookies)
        self.client = httpx.Client(base_url=self.api_base, timeout=30.0, cookies=_normalize_cookie_domains(cookies, self.api_base))

    def close(self) -> None:
        self.client.close()

    def save_cookies(self) -> None:
        self.cfg.cookies = _cookies_to_list(self.client.cookies)
        self.cfg.api_base = self.api_base
        save_config(self.cfg)

    def login_with_magic_link(self, login_url: str) -> None:
        sha_key = None
        try:
            qs = parse_qs(urlparse(login_url).query)
            sha_key = qs.get("sha_key", [None])[0]
        except Exception:
            sha_key = None

        if sha_key:
            resp = self.client.get(f"/api/login/{sha_key}/")
            if resp.status_code >= 400:
                raise ApiError("Login failed", resp.status_code, resp.text)
            self.save_cookies()
            return

        with httpx.Client(follow_redirects=True, timeout=30.0) as client:
            resp = client.get(login_url)
            if resp.status_code >= 400:
                raise ApiError("Login failed", resp.status_code, resp.text)
            self.client.cookies = _normalize_cookie_domains(client.cookies, self.api_base)
            self.save_cookies()

    def _request(self, method: str, url: str, **kwargs: Any) -> Any:
        retries = 0
        while True:
            resp = self.client.request(method, url, **kwargs)
            if 300 <= resp.status_code < 400 and "/api/logout" in resp.headers.get("location", ""):
                raise ApiError("Not authenticated (redirected to logout)", resp.status_code, resp.text)
            if resp.status_code == 429 and not self.no_retry and retries < 3:
                time.sleep(1.5 * (2**retries))
                retries += 1
                continue
            if resp.status_code >= 400:
                raise ApiError("Request failed", resp.status_code, resp.text)
            if "application/json" in resp.headers.get("content-type", ""):
                return resp.json()
            # try json anyway
            try:
                return resp.json()
            except Exception:
                return resp.text

    def _post_first(self, endpoints: list[str], payload: dict[str, Any]) -> Any:
        last_error: ApiError | None = None
        for ep in endpoints:
            try:
                return self._request("POST", ep, json=payload)
            except ApiError as e:
                last_error = e
            try:
                return self._request("POST", ep, data=payload)
            except ApiError as e:
                last_error = e
        if last_error:
            raise last_error
        raise ApiError("No endpoints tried")

    def session_info(self) -> Any:
        return self._request("GET", "/api/session_info")

    def get_digest(self, date: str | None = None) -> Any:
        if date:
            return self._request("GET", f"/api/?date={date}")
        return self._request("GET", "/api/")

    def get_trending(self, category: str = "ALL", days: int = 7, sort: str = "hype", asc: bool = False) -> Any:
        asc_val = "1" if asc else "0"
        return self._request(
            "GET",
            f"/api/trending?column={sort}&category={category}&ascending={asc_val}&dates={days}",
        )

    def search(self, query: str, sort: str | None = None, limit: int | None = None, offset: int | None = None) -> Any:
        payload: dict[str, Any] = {
            "search_prompt": query,
            "n_results": limit if limit is not None else 10,
            "p": offset if offset is not None else 0,
            "correct_search_prompt": True,
        }
        if sort:
            payload["orderBy"] = sort
        return self._request("POST", "/api/get_search_results/", json=payload)

    def semantic_search(self, text: str, limit: int | None = None, offset: int | None = None) -> Any:
        payload: dict[str, Any] = {
            "text_input": text,
            "embedding": "tfidf",
            "p": offset if offset is not None else 0,
        }
        if limit is not None:
            payload["n_results"] = limit
        return self._request("POST", "/api/semantic-search", json=payload)

    def interactions(self, type_: str = "all", sort: str = "ranking_score", asc: bool = False) -> Any:
        asc_val = "1" if asc else "0"
        return self._request(
            "GET",
            f"/api/interactions?column={sort}&type={type_}&ascending={asc_val}",
        )

    def bookmarks(self) -> Any:
        return self._request("GET", "/api/bookmarks")

    def bookmark_add(self, paper_id: str) -> Any:
        payload = {"paper_id": paper_id}
        try:
            return self._request("POST", "/api/bookmark_paper/", json=payload)
        except ApiError:
            return self._request("POST", "/api/bookmark_paper/", data=payload)

    def bookmark_remove(self, paper_id: str) -> Any:
        payload = {"paper_id": paper_id}
        try:
            return self._request("POST", "/api/unbookmark_paper/", json=payload)
        except ApiError:
            return self._request("POST", "/api/unbookmark_paper/", data=payload)

    def collections_list(self) -> Any:
        try:
            return self._request("GET", "/api/get_all_user_collections")
        except ApiError:
            return self._request("GET", "/api/collections")

    def collections_expanded(self) -> Any:
        return self._request("GET", "/api/get_expanded_collections")

    def collections_map(self) -> Any:
        return self._request("GET", "/api/collections")

    def collection_create(self, name: str) -> Any:
        payload = {"name": name, "collection_name": name}
        endpoints = [
            "/api/create_collection/",
            "/api/collections",
            "/api/collection-create/",
        ]
        return self._post_first(endpoints, payload)

    def collection_rename(self, collection_id: str, new_name: str) -> Any:
        payload = {
            "collection_id": collection_id,
            "id": collection_id,
            "name": new_name,
            "new_name": new_name,
        }
        endpoints = [
            "/api/rename_collection/",
            "/api/collection-rename/",
            "/api/collections/rename",
        ]
        return self._post_first(endpoints, payload)

    def collection_delete(self, collection_id: str) -> Any:
        payload = {"collection_id": collection_id, "id": collection_id}
        endpoints = [
            "/api/delete_collection/",
            "/api/collection-delete/",
            "/api/collections/delete",
        ]
        return self._post_first(endpoints, payload)

    def collection_add_paper(self, collection_id: str, paper_id: str) -> Any:
        payload = {"collection_id": collection_id, "paper_id": paper_id}
        endpoints = [
            "/api/add_paper_to_collection/",
            "/api/collection-add-paper/",
            "/api/add_to_collection/",
        ]
        return self._post_first(endpoints, payload)

    def collection_remove_paper(self, collection_id: str, paper_id: str) -> Any:
        payload = {"collection_id": collection_id, "paper_id": paper_id}
        endpoints = [
            "/api/remove_paper_from_collection/",
            "/api/collection-remove-paper/",
            "/api/remove_from_collection/",
        ]
        return self._post_first(endpoints, payload)

    def collection_papers(self, collection_id: str, limit: int | None = None, offset: int | None = None) -> Any:
        params: dict[str, Any] = {"collection_id": collection_id}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        try:
            return self._request("GET", "/api/collection-papers", params=params)
        except ApiError:
            # fallback without paging
            return self._request("GET", "/api/collection-papers", params={"collection_id": collection_id})

    def collections_similar(self, collection_ids: list[str], limit: int | None = None, offset: int | None = None) -> Any:
        schemas = [
            "json_collection_ids_p",
            "json_collection_ids",
            "json_collection_id",
            "form_collection_ids",
            "get_params",
        ]
        if self.cfg.collections_similar_schema:
            schemas = [self.cfg.collections_similar_schema] + [s for s in schemas if s != self.cfg.collections_similar_schema]

        for schema in schemas:
            try:
                data = self._collections_similar_with_schema(schema, collection_ids, limit, offset)
                if _is_paper_list(data):
                    self.cfg.collections_similar_schema = schema
                    save_config(self.cfg)
                    return data
            except ApiError:
                continue
        raise ApiError("Unable to fetch similar papers for collections")

    def _collections_similar_with_schema(
        self, schema: str, collection_ids: list[str], limit: int | None, offset: int | None
    ) -> Any:
        if schema == "json_collection_ids_p":
            payload: dict[str, Any] = {"collectionIds": collection_ids, "p": offset if offset is not None else 0}
            if limit is not None:
                payload["n_results"] = limit
            return self._request("POST", "/api/get_collections_similar_papers/", json=payload)
        if schema == "json_collection_ids":
            payload: dict[str, Any] = {"collection_ids": collection_ids}
            if limit is not None:
                payload["limit"] = limit
            if offset is not None:
                payload["offset"] = offset
            return self._request("POST", "/api/get_collections_similar_papers/", json=payload)
        if schema == "json_collection_id" and len(collection_ids) == 1:
            payload = {"collection_id": collection_ids[0]}
            if limit is not None:
                payload["limit"] = limit
            if offset is not None:
                payload["offset"] = offset
            return self._request("POST", "/api/get_collections_similar_papers/", json=payload)
        if schema == "form_collection_ids":
            payload = {"collection_ids": ",".join(collection_ids)}
            if limit is not None:
                payload["limit"] = limit
            if offset is not None:
                payload["offset"] = offset
            return self._request("POST", "/api/get_collections_similar_papers/", data=payload)
        if schema == "get_params":
            params = {"collection_id": ",".join(collection_ids)}
            if limit is not None:
                params["limit"] = limit
            if offset is not None:
                params["offset"] = offset
            return self._request("GET", "/api/get_collections_similar_papers/", params=params)
        raise ApiError("Unknown schema")

    def conference_list(self) -> Any:
        return self._request("GET", "/api/conference_list")

    def conference_explorer(self, query: str | None = None, sort: str | None = None) -> Any:
        params: dict[str, Any] = {}
        if query:
            params["query"] = query
        if sort:
            params["sort"] = sort
        return self._request("GET", "/api/conference-explorer", params=params)
