"""CLI commands for locking and unlocking a vault."""

from __future__ import annotations

import click

from envault.lock import lock_vault, unlock_vault, is_locked, get_lock_info


@click.group("lock", help="Lock or unlock a vault to prevent writes.")
def lock_group() -> None:
    pass


@lock_group.command("set", help="Lock the vault.")
@click.option("--vault", default="vault.json", show_default=True, help="Path to vault file.")
@click.option("--reason", default=None, help="Optional reason for locking.")
def set_cmd(vault: str, reason: str | None) -> None:
    try:
        entry = lock_vault(vault, reason=reason)
        click.echo(f"Vault locked at {entry['locked_at']}.")
        if entry["reason"]:
            click.echo(f"Reason: {entry['reason']}")
    except FileExistsError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@lock_group.command("unset", help="Unlock the vault.")
@click.option("--vault", default="vault.json", show_default=True, help="Path to vault file.")
def unset_cmd(vault: str) -> None:
    removed = unlock_vault(vault)
    if removed:
        click.echo("Vault unlocked.")
    else:
        click.echo("Vault was not locked.", err=True)
        raise SystemExit(1)


@lock_group.command("status", help="Show whether the vault is locked.")
@click.option("--vault", default="vault.json", show_default=True, help="Path to vault file.")
def status_cmd(vault: str) -> None:
    info = get_lock_info(vault)
    if info is None:
        click.echo("Vault is UNLOCKED.")
    else:
        click.echo(f"Vault is LOCKED since {info['locked_at']}.")
        if info.get("reason"):
            click.echo(f"Reason: {info['reason']}")
