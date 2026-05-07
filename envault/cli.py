"""Main CLI entry point for envault."""

import click

from envault.vault import load_vault, save_vault, set_secret, get_secret, delete_secret
from envault.export import import_dotenv_file, export_dotenv_file
from envault.audit import record_event
from envault.cli_audit import audit_group
from envault.cli_rotate import rotate_group
from envault.cli_diff import diff_group


def _prompt_password(confirm: bool = True) -> str:
    return click.prompt(
        "Password",
        hide_input=True,
        confirmation_prompt=confirm,
    )


@click.group()
def cli():
    """envault — encrypt and sync your .env secrets."""


@cli.command()
@click.argument("key")
@click.argument("value")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def set(key, value, vault_path):
    """Set a secret in the vault."""
    password = _prompt_password(confirm=False)
    vault = load_vault(vault_path)
    vault = set_secret(vault, key, value, password)
    save_vault(vault, vault_path)
    record_event("set", {"key": key, "vault": vault_path})
    click.echo(f"Secret '{key}' saved.")


@cli.command()
@click.argument("key")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def get(key, vault_path):
    """Get a secret from the vault."""
    password = _prompt_password(confirm=False)
    vault = load_vault(vault_path)
    try:
        value = get_secret(vault, key, password)
        record_event("get", {"key": key, "vault": vault_path})
        click.echo(value)
    except KeyError:
        raise click.ClickException(f"Key '{key}' not found.")
    except Exception as exc:
        raise click.ClickException(str(exc))


@cli.command()
@click.argument("key")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def delete(key, vault_path):
    """Delete a secret from the vault."""
    password = _prompt_password(confirm=False)
    vault = load_vault(vault_path)
    vault = delete_secret(vault, key)
    save_vault(vault, vault_path)
    record_event("delete", {"key": key, "vault": vault_path})
    click.echo(f"Secret '{key}' deleted.")


@cli.command(name="import")
@click.argument("dotenv_path", default=".env")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def import_cmd(dotenv_path, vault_path):
    """Import secrets from a .env file into the vault."""
    password = _prompt_password(confirm=True)
    vault = load_vault(vault_path)
    count = import_dotenv_file(vault, dotenv_path, password, vault_path)
    record_event("import", {"dotenv": dotenv_path, "vault": vault_path, "count": count})
    click.echo(f"Imported {count} secrets from '{dotenv_path}'.")


@cli.command(name="export")
@click.argument("dotenv_path", default=".env")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def export_cmd(dotenv_path, vault_path):
    """Export secrets from the vault to a .env file."""
    password = _prompt_password(confirm=False)
    vault = load_vault(vault_path)
    count = export_dotenv_file(vault, dotenv_path, password)
    record_event("export", {"dotenv": dotenv_path, "vault": vault_path, "count": count})
    click.echo(f"Exported {count} secrets to '{dotenv_path}'.")


cli.add_command(audit_group)
cli.add_command(rotate_group)
cli.add_command(diff_group)
