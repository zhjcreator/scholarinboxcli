"""Config and session storage for scholarinboxcli."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "scholarinboxcli"
CONFIG_PATH = CONFIG_DIR / "config.json"


@dataclass
class Config:
    api_base: str = "https://api.scholar-inbox.com"
    base_url: str = "https://www.scholar-inbox.com"
    cookies: list[dict[str, Any]] | None = None
    collections_similar_schema: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "api_base": self.api_base,
            "base_url": self.base_url,
            "cookies": self.cookies,
            "collections_similar_schema": self.collections_similar_schema,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Config":
        return cls(
            api_base=data.get("api_base", cls.api_base),
            base_url=data.get("base_url", cls.base_url),
            cookies=data.get("cookies"),
            collections_similar_schema=data.get("collections_similar_schema"),
        )


def load_config() -> Config:
    if not CONFIG_PATH.exists():
        return Config()
    try:
        data = json.loads(CONFIG_PATH.read_text())
    except Exception:
        return Config()
    return Config.from_dict(data)


def save_config(cfg: Config) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg.to_dict(), indent=2))
