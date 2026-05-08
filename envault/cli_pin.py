"""CLI commands for pinning and unpinning vault secrets."""

from __future__ import annotations

import click

from envault.pin import clear_pins, is_pinned, list_pins, pin_key, unpin_key

DEFAULT_VAULT = "vault.enc"


@click.group("pin")
def pin_group() -> None:
    """Pin secrets to prevent accidental modification or deletion."""


@pin_group.command("set")
@click.argument("key")
@click.option("--reason", "-r", default="", help="Optional reason for pinning.")
@click.option("--vault", default=DEFAULT_VAULT, help="Path to vault file.")
def set_cmd(key: str, reason: str, vault: str) -> None:
    """Pin KEY so it cannot be modified or deleted without unpinning first."""
    entry = pin_key(vault, key, reason=reason)
    msg = f"Pinned '{entry['key']}'"
    if reason:
        msg += f" — {reason}"
    click.echo(msg)


@pin_group.command("unset")
@click.argument("key")
@click.option("--vault", default=DEFAULT_VAULT, help="Path to vault file.")
def unset_cmd(key: str, vault: str) -> None:
    """Unpin KEY, allowing it to be modified or deleted again."""
    removed = unpin_key(vault, key)
    if removed:
        click.echo(f"Unpinned '{key}'.")
    else:
        click.echo(f"'{key}' was not pinned.", err=True)


@pin_group.command("status")
@click.argument("key")
@click.option("--vault", default=DEFAULT_VAULT, help="Path to vault file.")
def status_cmd(key: str, vault: str) -> None:
    """Show whether KEY is currently pinned."""
    if is_pinned(vault, key):
        click.echo(f"'{key}' is PINNED.")
    else:
        click.echo(f"'{key}' is not pinned.")


@pin_group.command("list")
@click.option("--vault", default=DEFAULT_VAULT, help="Path to vault file.")
def list_cmd(vault: str) -> None:
    """List all currently pinned keys."""
    pins = list_pins(vault)
    if not pins:
        click.echo("No keys are pinned.")
        return
    for entry in pins:
        line = entry["key"]
        if entry.get("reason"):
            line += f"  ({entry['reason']})"
        click.echo(line)


@pin_group.command("clear")
@click.option("--vault", default=DEFAULT_VAULT, help="Path to vault file.")
def clear_cmd(vault: str) -> None:
    """Remove all pins from the vault."""
    count = clear_pins(vault)
    click.echo(f"Cleared {count} pin(s).")
