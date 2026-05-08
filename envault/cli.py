"""Main CLI entry-point for envault."""

from __future__ import annotations

from pathlib import Path

import click

from envault.vault import set_secret, get_secret, delete_secret, list_secrets
from envault.audit import record_event


def _prompt_password(confirm: bool = True) -> str:
    return click.prompt(
        "Password",
        hide_input=True,
        confirmation_prompt=confirm,
    )


@click.group()
def cli() -> None:
    """envault — encrypted .env vault CLI."""


@cli.command()
@click.argument("key")
@click.argument("value")
@click.option("--vault", default="vault.json", show_default=True, type=click.Path(path_type=Path))
def set(key: str, value: str, vault: Path) -> None:
    """Store a secret KEY=VALUE in the vault."""
    password = _prompt_password(confirm=False)
    set_secret(vault, password, key, value)
    record_event("set", {"key": key})
    click.echo(f"Set {key}")


@cli.command()
@click.argument("key")
@click.option("--vault", default="vault.json", show_default=True, type=click.Path(path_type=Path))
def get(key: str, vault: Path) -> None:
    """Retrieve a secret by KEY from the vault."""
    password = _prompt_password(confirm=False)
    value = get_secret(vault, password, key)
    if value is None:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    click.echo(value)


@cli.command()
@click.argument("key")
@click.option("--vault", default="vault.json", show_default=True, type=click.Path(path_type=Path))
def delete(key: str, vault: Path) -> None:
    """Delete a secret by KEY from the vault."""
    password = _prompt_password(confirm=False)
    removed = delete_secret(vault, password, key)
    if not removed:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    record_event("delete", {"key": key})
    click.echo(f"Deleted {key}")


@cli.command(name="list")
@click.option("--vault", default="vault.json", show_default=True, type=click.Path(path_type=Path))
def list_cmd(vault: Path) -> None:
    """List all keys stored in the vault."""
    password = _prompt_password(confirm=False)
    keys = list_secrets(vault, password)
    if not keys:
        click.echo("No secrets stored.")
    else:
        for k in sorted(keys):
            click.echo(k)


# ---------------------------------------------------------------------------
# Register sub-command groups from feature modules
# ---------------------------------------------------------------------------
from envault.cli_audit import audit_group          # noqa: E402
from envault.cli_rotate import rotate_group        # noqa: E402
from envault.cli_diff import diff_group            # noqa: E402
from envault.cli_search import search_group        # noqa: E402
from envault.cli_tags import tags_group            # noqa: E402
from envault.cli_snapshots import snapshot_group   # noqa: E402
from envault.cli_rename import rename_group        # noqa: E402
from envault.cli_history import history_group      # noqa: E402
from envault.cli_template import template_group    # noqa: E402
from envault.cli_ttl import ttl_group              # noqa: E402
from envault.cli_lock import lock_group            # noqa: E402
from envault.cli_pin import pin_group              # noqa: E402
from envault.cli_profile import profile_group      # noqa: E402
from envault.cli_watch import watch_group          # noqa: E402

cli.add_command(audit_group)
cli.add_command(rotate_group)
cli.add_command(diff_group)
cli.add_command(search_group)
cli.add_command(tags_group)
cli.add_command(snapshot_group)
cli.add_command(rename_group)
cli.add_command(history_group)
cli.add_command(template_group)
cli.add_command(ttl_group)
cli.add_command(lock_group)
cli.add_command(pin_group)
cli.add_command(profile_group)
cli.add_command(watch_group)
