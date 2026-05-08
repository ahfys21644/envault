"""Main CLI entry point for envault."""

import click
from pathlib import Path

from envault.vault import set_secret, get_secret, delete_secret, list_keys
from envault.cli_audit import audit_group
from envault.cli_rotate import rotate_group
from envault.cli_diff import diff_group
from envault.cli_search import search_group
from envault.cli_tags import tags_group
from envault.cli_snapshots import snapshot_group
from envault.cli_rename import rename_group
from envault.cli_history import history_group
from envault.cli_template import template_group
from envault.cli_ttl import ttl_group

_DEFAULT_VAULT = Path(".envault")


def _prompt_password(confirm: bool = False) -> str:
    if confirm:
        return click.prompt("Password", hide_input=True, confirmation_prompt=True)
    return click.prompt("Password", hide_input=True)


@click.group()
def cli():
    """envault — encrypted .env secret manager."""
    pass


@cli.command()
@click.argument("key")
@click.argument("value")
@click.option("--vault", default=str(_DEFAULT_VAULT), show_default=True)
def set(key: str, value: str, vault: str):
    """Store a secret in the vault."""
    password = _prompt_password(confirm=False)
    set_secret(Path(vault), key, value, password)
    click.echo(f"Secret '{key}' stored.")


@cli.command()
@click.argument("key")
@click.option("--vault", default=str(_DEFAULT_VAULT), show_default=True)
def get(key: str, vault: str):
    """Retrieve a secret from the vault."""
    password = _prompt_password(confirm=False)
    value = get_secret(Path(vault), key, password)
    if value is None:
        click.echo(f"Key '{key}' not found.", err=True)
    else:
        click.echo(value)


@cli.command()
@click.argument("key")
@click.option("--vault", default=str(_DEFAULT_VAULT), show_default=True)
def delete(key: str, vault: str):
    """Delete a secret from the vault."""
    password = _prompt_password(confirm=False)
    deleted = delete_secret(Path(vault), key, password)
    if deleted:
        click.echo(f"Secret '{key}' deleted.")
    else:
        click.echo(f"Key '{key}' not found.", err=True)


@cli.command(name="list")
@click.option("--vault", default=str(_DEFAULT_VAULT), show_default=True)
def list_cmd(vault: str):
    """List all keys in the vault."""
    password = _prompt_password(confirm=False)
    keys = list_keys(Path(vault), password)
    if not keys:
        click.echo("Vault is empty.")
    else:
        for k in keys:
            click.echo(k)


cli.add_command(audit_group, name="audit")
cli.add_command(rotate_group, name="rotate")
cli.add_command(diff_group, name="diff")
cli.add_command(search_group, name="search")
cli.add_command(tags_group, name="tags")
cli.add_command(snapshot_group, name="snapshot")
cli.add_command(rename_group, name="rename")
cli.add_command(history_group, name="history")
cli.add_command(template_group, name="template")
cli.add_command(ttl_group, name="ttl")


if __name__ == "__main__":
    cli()
