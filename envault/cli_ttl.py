"""CLI commands for managing secret TTLs."""

import click
from pathlib import Path

from envault.ttl import set_ttl, get_ttl, remove_ttl, list_expired, purge_expired
from envault.cli import _prompt_password

_DEFAULT_VAULT = Path(".envault")


@click.group("ttl", help="Manage time-to-live for secrets.")
def ttl_group():
    pass


@ttl_group.command("set", help="Set TTL (seconds) for a key.")
@click.argument("key")
@click.argument("seconds", type=int)
@click.option("--vault", default=str(_DEFAULT_VAULT), show_default=True)
def set_cmd(key: str, seconds: int, vault: str):
    vault_path = Path(vault)
    result = set_ttl(vault_path, key, seconds)
    import datetime
    exp = datetime.datetime.fromtimestamp(result["expires_at"]).strftime("%Y-%m-%d %H:%M:%S")
    click.echo(f"TTL set for '{key}': expires at {exp} ({seconds}s from now).")


@ttl_group.command("get", help="Show TTL info for a key.")
@click.argument("key")
@click.option("--vault", default=str(_DEFAULT_VAULT), show_default=True)
def get_cmd(key: str, vault: str):
    info = get_ttl(Path(vault), key)
    if info is None:
        click.echo(f"No TTL set for '{key}'.")
        return
    status = "EXPIRED" if info["expired"] else f"{info['remaining_seconds']:.1f}s remaining"
    click.echo(f"'{key}' TTL: {status}")


@ttl_group.command("remove", help="Remove TTL for a key.")
@click.argument("key")
@click.option("--vault", default=str(_DEFAULT_VAULT), show_default=True)
def remove_cmd(key: str, vault: str):
    removed = remove_ttl(Path(vault), key)
    if removed:
        click.echo(f"TTL removed for '{key}'.")
    else:
        click.echo(f"No TTL was set for '{key}'.")


@ttl_group.command("list-expired", help="List keys whose TTL has elapsed.")
@click.option("--vault", default=str(_DEFAULT_VAULT), show_default=True)
def list_expired_cmd(vault: str):
    keys = list_expired(Path(vault))
    if not keys:
        click.echo("No expired keys found.")
    else:
        click.echo(f"Expired keys ({len(keys)}):")
        for k in keys:
            click.echo(f"  - {k}")


@ttl_group.command("purge", help="Delete all expired secrets from the vault.")
@click.option("--vault", default=str(_DEFAULT_VAULT), show_default=True)
def purge_cmd(vault: str):
    password = _prompt_password(confirm=False)
    purged = purge_expired(Path(vault), password)
    if not purged:
        click.echo("No expired secrets to purge.")
    else:
        click.echo(f"Purged {len(purged)} expired secret(s): {', '.join(purged)}")
