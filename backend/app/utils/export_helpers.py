"""Export helper functions — formatting, templating."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def flatten_dict(d: dict[str, Any], parent_key: str = "", sep: str = ".") -> dict[str, Any]:
    """Flatten a nested dictionary for CSV export."""
    items: list[tuple[str, Any]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, str(v)))
        else:
            items.append((new_key, v))
    return dict(items)


def generate_filename(prefix: str, extension: str) -> str:
    """Generate a timestamped filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def truncate_for_display(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis for display."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
