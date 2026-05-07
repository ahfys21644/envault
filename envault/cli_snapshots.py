"""CLI commands for vault snapshot management."""

from __future__ import annotations

import time
from pathlib import Path

import click

from envault.cli import _prompt_password
from envault.snapshots import (
    create_snapshot,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
)

DEFAULT_VAULT = Path(".envault")


@click.group("snapshot")
def snapshot_group() -> None:
    """Create and restore vault snapshots."""


@snapshot_group.command("create")
@click.argument("label")
@click.option("--vault", default=str(DEFAULT_VAULT), show_default=True)
def create_cmd(label: str, vault: str) -> None:
    """Capture the current vault state as LABEL."""
    password = _prompt_password(confirm=False)
    entry = create_snapshot(Path(vault), password, label)
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry["timestamp"]))
    click.echo(f"Snapshot '{label}' created at {ts}.")


@snapshot_group.command("restore")
@click.argument("label")
@click.option("--vault", default=str(DEFAULT_VAULT), show_default=True)
def restore_cmd(label: str, vault: str) -> None:
    """Restore the vault to the state saved as LABEL."""
    password = _prompt_password(confirm=False)
    try:
        count = restore_snapshot(Path(vault), password, label)
        click.echo(f"Restored {count} secret(s) from snapshot '{label}'.")
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc


@snapshot_group.command("list")
@click.option("--vault", default=str(DEFAULT_VAULT), show_default=True)
def list_cmd(vault: str) -> None:
    """List all available snapshots."""
    entries = list_snapshots(Path(vault))
    if not entries:
        click.echo("No snapshots found.")
        return
    for entry in entries:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry["timestamp"]))
        count = len(entry["data"])
        click.echo(f"  {entry['label']:<20} {ts}  ({count} secrets)")


@snapshot_group.command("delete")
@click.argument("label")
@click.option("--vault", default=str(DEFAULT_VAULT), show_default=True)
def delete_cmd(label: str, vault: str) -> None:
    """Delete snapshot LABEL."""
    removed = delete_snapshot(Path(vault), label)
    if removed:
        click.echo(f"Snapshot '{label}' deleted.")
    else:
        raise click.ClickException(f"Snapshot '{label}' not found.")
