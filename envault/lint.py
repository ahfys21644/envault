"""Lint .env files for common issues before importing into the vault."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class LintIssue:
    line_number: int
    line: str
    message: str
    severity: str  # "error" | "warning"


@dataclass
class LintResult:
    path: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")


_VALID_KEY_RE = re.compile(r'^[A-Z_][A-Z0-9_]*$')
_KEY_VALUE_RE = re.compile(r'^([^=]+)=(.*)$')


def lint_dotenv_file(path: str | Path) -> LintResult:
    """Parse and lint a .env file, returning a LintResult with any issues found."""
    p = Path(path)
    result = LintResult(path=str(p))

    if not p.exists():
        result.issues.append(LintIssue(0, "", f"File not found: {p}", "error"))
        return result

    seen_keys: dict[str, int] = {}

    for lineno, raw in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        m = _KEY_VALUE_RE.match(line)
        if not m:
            result.issues.append(LintIssue(lineno, raw, "Line is not a valid KEY=VALUE pair", "error"))
            continue

        key, value = m.group(1).strip(), m.group(2)

        if not _VALID_KEY_RE.match(key):
            result.issues.append(LintIssue(lineno, raw,
                f"Key '{key}' should be uppercase with only letters, digits, and underscores",
                "warning"))

        if key in seen_keys:
            result.issues.append(LintIssue(lineno, raw,
                f"Duplicate key '{key}' (first seen on line {seen_keys[key]})",
                "warning"))
        else:
            seen_keys[key] = lineno

        stripped = value.strip()
        if len(stripped) >= 2 and stripped[0] in ('"', "'") and stripped[-1] != stripped[0]:
            result.issues.append(LintIssue(lineno, raw,
                f"Value for '{key}' appears to have an unclosed quote",
                "error"))

    return result


def format_lint_result(result: LintResult) -> str:
    """Return a human-readable summary of a LintResult."""
    if not result.issues:
        return f"{result.path}: OK (no issues found)"

    lines = [f"{result.path}: {result.error_count} error(s), {result.warning_count} warning(s)"]
    for issue in result.issues:
        prefix = "[ERROR]  " if issue.severity == "error" else "[WARN]   "
        lines.append(f"  Line {issue.line_number:>4}: {prefix}{issue.message}")
    return "\n".join(lines)
