"""JSON formatting helpers."""

from __future__ import annotations

import json
import sys
from typing import Any


def format_json(data: Any) -> str:
    if sys.stdout.isatty():
        return json.dumps(data, indent=2, ensure_ascii=True)
    return json.dumps(data, separators=(",", ":"), ensure_ascii=True)
