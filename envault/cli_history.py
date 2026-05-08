"""CLI commands for inspecting per-key change history."""

from __future__ import annotations

import click

from envault.history import (
    clear_key_history,
    get_key_history,
    list_keys_with_history,
)

_DEFAULT_VAULT = "vault.enc"


@click.group("history")
def history_group() -> None:
    """View and manage per-key change history."""


@history_group.command("show")
@click.argument("key")
@click.option("--vault", default=_DEFAULT_VAULT, show_default=True)
def show_cmd(key: str, vault: str) -> None:
    """Show the change history for KEY."""
    entries = get_key_history(vault, key)
    if not entries:
        click.echo(f"No history found for '{key}'.")
        return
    click.echo(f"History for '{key}' ({len(entries)} entries):")
    for i, entry in enumerate(entries, 1):
        line = f"  {i}. [{entry['timestamp']}] {entry['action']}"
        if "old_value" in entry:
            line += f"  (was: {entry['old_value']})"
        click.echo(line)


@history_group.command("list")
@click.option("--vault", default=_DEFAULT_VAULT, show_default=True)
def list_cmd(vault: str) -> None:
    """List all keys that have recorded history."""
    keys = list_keys_with_history(vault)
    if not keys:
        click.echo("No history recorded yet.")
        return
    click.echo(f"Keys with history ({len(keys)}):")
    for key in keys:
        click.echo(f"  {key}")


@history_group.command("clear")
@click.argument("key")
@click.option("--vault", default=_DEFAULT_VAULT, show_default=True)
def clear_cmd(key: str, vault: str) -> None:
    """Clear the change history for KEY."""
    removed = clear_key_history(vault, key)
    if removed == 0:
        click.echo(f"No history to clear for '{key}'.")
    else:
        click.echo(f"Cleared {removed} history entries for '{key}'.")
