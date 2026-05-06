"""Export and import .env file functionality for envault."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional


def parse_dotenv(content: str) -> Dict[str, str]:
    """Parse the contents of a .env file into a key-value dictionary.

    Supports:
      - KEY=VALUE
      - KEY="VALUE WITH SPACES"
      - KEY='VALUE WITH SPACES'
      - Lines beginning with # are treated as comments and ignored.
      - Empty lines are ignored.
    """
    result: Dict[str, str] = {}
    pattern = re.compile(
        r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*="
        r"\s*(?P<value>['\"]?)(?P<inner>.*?)(?P=value)\s*$"
    )
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = pattern.match(stripped)
        if match:
            result[match.group("key")] = match.group("inner")
    return result


def render_dotenv(secrets: Dict[str, str]) -> str:
    """Render a dictionary of secrets as a .env file string."""
    lines = []
    for key, value in sorted(secrets.items()):
        # Quote values that contain spaces or special characters
        if any(c in value for c in (" ", "\t", "'", '"', "#", "$")):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def import_dotenv_file(filepath: Path) -> Dict[str, str]:
    """Read a .env file from disk and return its key-value pairs."""
    if not filepath.exists():
        raise FileNotFoundError(f".env file not found: {filepath}")
    content = filepath.read_text(encoding="utf-8")
    return parse_dotenv(content)


def export_dotenv_file(secrets: Dict[str, str], filepath: Path) -> None:
    """Write secrets to a .env file on disk."""
    content = render_dotenv(secrets)
    filepath.write_text(content, encoding="utf-8")
