"""Template rendering: substitute vault secrets into template files."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envault.vault import get_secret

# Matches {{ VAR_NAME }} with optional whitespace
_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


@dataclass
class RenderResult:
    output: str
    substituted: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.missing) == 0


def render_template(template: str, secrets: Dict[str, str]) -> RenderResult:
    """Replace {{ KEY }} placeholders in *template* with values from *secrets*."""
    substituted: List[str] = []
    missing: List[str] = []

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        if key in secrets:
            substituted.append(key)
            return secrets[key]
        missing.append(key)
        return match.group(0)  # leave placeholder intact

    output = _PLACEHOLDER_RE.sub(replacer, template)
    return RenderResult(output=output, substituted=substituted, missing=missing)


def render_template_file(
    template_path: Path,
    vault_path: Path,
    password: str,
    output_path: Path | None = None,
) -> RenderResult:
    """Read a template file, substitute secrets from *vault_path*, optionally write output."""
    template = template_path.read_text(encoding="utf-8")

    # Collect all secrets from vault
    from envault.vault import load_vault  # local import to avoid circular deps
    from envault.crypto import decrypt

    raw = load_vault(vault_path)
    secrets: Dict[str, str] = {}
    for key, ciphertext in raw.items():
        try:
            secrets[key] = decrypt(ciphertext, password)
        except Exception:
            pass  # skip keys that can't be decrypted

    result = render_template(template, secrets)

    if output_path is not None:
        output_path.write_text(result.output, encoding="utf-8")

    return result
