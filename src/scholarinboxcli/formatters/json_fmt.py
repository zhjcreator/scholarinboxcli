"""JSON formatting helpers."""

from __future__ import annotations

import json
from typing import Any


def format_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=True)
