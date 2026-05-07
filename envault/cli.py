"""Main CLI entry point for envault."""

from __future__ import annotations

import click

from envault.vault import load_vault, save_vault, set_secret, get_secret, delete_secret
from envault.export import import_dotenv_file, export_dotenv_file


def _prompt_password(confirm: bool = True) -> str:
    """Prompt for a master password, optionally asking for confirmation."""
    return click.prompt(
        "Master password",
        hide_input=True,
        confirmation_prompt=confirm,
    )


@click.group()
def cli() -> None:
    """envault — encrypt and sync your .env secrets."""


@cli.command()
@click.argument("key")
@click.argument("value")
@click.option("--vault", default=".envault", show_default=True)
def set(key: str, value: str, vault: str) -> None:  # noqa: A001
    """Store a secret KEY=VALUE in the vault."""
    password = _prompt_password(confirm=False)
    data = load_vault(vault)
    set_secret(data, password, key, value)
    save_vault(vault, data)
    click.echo(f"Set {key}")


@cli.command()
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def get(key: str, vault: str) -> None:
    """Retrieve a secret by KEY."""
    password = _prompt_password(confirm=False)
    data = load_vault(vault)
    try:
        value = get_secret(data, password, key)
        click.echo(value)
    except KeyError:
        raise click.ClickException(f"Key '{key}' not found.")


@cli.command()
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
def delete(key: str, vault: str) -> None:
    """Delete a secret by KEY."""
    password = _prompt_password(confirm=False)
    data = load_vault(vault)
    try:
        delete_secret(data, key)
        save_vault(vault, data)
        click.echo(f"Deleted {key}")
    except KeyError:
        raise click.ClickException(f"Key '{key}' not found.")


@cli.command(name="import")
@click.argument("dotenv_file", type=click.Path(exists=True))
@click.option("--vault", default=".envault", show_default=True)
def import_cmd(dotenv_file: str, vault: str) -> None:
    """Import secrets from a .env FILE into the vault."""
    password = _prompt_password(confirm=False)
    count = import_dotenv_file(dotenv_file, vault, password)
    click.echo(f"Imported {count} secret(s) from {dotenv_file}")


@cli.command(name="export")
@click.argument("dotenv_file")
@click.option("--vault", default=".envault", show_default=True)
def export_cmd(dotenv_file: str, vault: str) -> None:
    """Export secrets from the vault to a .env FILE."""
    password = _prompt_password(confirm=False)
    count = export_dotenv_file(vault, dotenv_file, password)
    click.echo(f"Exported {count} secret(s) to {dotenv_file}")


# Register sub-command groups
from envault.cli_audit import audit_group  # noqa: E402
from envault.cli_rotate import rotate_group  # noqa: E402
from envault.cli_diff import diff_group  # noqa: E402
from envault.cli_search import search_group  # noqa: E402

cli.add_command(audit_group)
cli.add_command(rotate_group)
cli.add_command(diff_group)
cli.add_command(search_group)


if __name__ == "__main__":
    cli()
