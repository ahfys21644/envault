"""Command-line interface for envault."""

import click
from pathlib import Path
from getpass import getpass

from envault.vault import (
    set_secret, get_secret, delete_secret,
    list_keys, load_vault, DEFAULT_VAULT,
)


def _prompt_password(confirm: bool = False) -> str:
    pwd = getpass("Vault password: ")
    if confirm:
        pwd2 = getpass("Confirm password: ")
        if pwd != pwd2:
            raise click.ClickException("Passwords do not match.")
    return pwd


@click.group()
@click.option("--vault", default=str(DEFAULT_VAULT), show_default=True,
              help="Path to the vault file.")
@click.pass_context
def cli(ctx, vault):
    """envault — encrypt and sync .env secrets."""
    ctx.ensure_object(dict)
    ctx.obj["vault"] = Path(vault)


@cli.command()
@click.argument("key")
@click.argument("value")
@click.pass_context
def set(ctx, key, value):
    """Store or update a secret KEY=VALUE."""
    pwd = _prompt_password(confirm=not ctx.obj["vault"].exists())
    set_secret(key, value, ctx.obj["vault"], pwd)
    click.echo(f"✓ '{key}' saved.")


@cli.command()
@click.argument("key")
@click.pass_context
def get(ctx, key):
    """Print the value of a secret KEY."""
    pwd = _prompt_password()
    val = get_secret(key, ctx.obj["vault"], pwd)
    if val is None:
        raise click.ClickException(f"Key '{key}' not found.")
    click.echo(val)


@cli.command()
@click.argument("key")
@click.pass_context
def delete(ctx, key):
    """Remove a secret by KEY."""
    pwd = _prompt_password()
    removed = delete_secret(key, ctx.obj["vault"], pwd)
    if not removed:
        raise click.ClickException(f"Key '{key}' not found.")
    click.echo(f"✓ '{key}' deleted.")


@cli.command(name="list")
@click.pass_context
def list_cmd(ctx):
    """List all stored secret keys."""
    pwd = _prompt_password()
    keys = list_keys(ctx.obj["vault"], pwd)
    if not keys:
        click.echo("(vault is empty)")
    else:
        click.echo("\n".join(keys))


@cli.command()
@click.argument("env_file", default=".env", type=click.Path())
@click.pass_context
def export(ctx, env_file):
    """Write all secrets to an .env file."""
    pwd = _prompt_password()
    data = load_vault(ctx.obj["vault"], pwd)
    lines = [f"{k}={v}" for k, v in sorted(data.items())]
    Path(env_file).write_text("\n".join(lines) + "\n", encoding="utf-8")
    click.echo(f"✓ Exported {len(lines)} secret(s) to '{env_file}'.")


if __name__ == "__main__":
    cli()
