"""CLI commands for managing secret tags."""

from __future__ import annotations

import click

from envault.cli import _prompt_password
from envault.tags import add_tag, remove_tag, list_tags, keys_for_tag


@click.group("tags", help="Manage tags on vault secrets.")
def tags_group() -> None:  # pragma: no cover
    pass


@tags_group.command("add", help="Add a tag to a secret key.")
@click.argument("key")
@click.argument("tag")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
@click.option("--password", default=None, help="Vault password (prompted if omitted).")
def add_cmd(key: str, tag: str, vault: str, password: str | None) -> None:
    pw = password or _prompt_password(confirm=False)
    add_tag(vault, pw, key, tag)
    click.echo(f"Tag '{tag}' added to '{key}'.")


@tags_group.command("remove", help="Remove a tag from a secret key.")
@click.argument("key")
@click.argument("tag")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", default=None)
def remove_cmd(key: str, tag: str, vault: str, password: str | None) -> None:
    pw = password or _prompt_password(confirm=False)
    removed = remove_tag(vault, pw, key, tag)
    if removed:
        click.echo(f"Tag '{tag}' removed from '{key}'.")
    else:
        click.echo(f"Tag '{tag}' was not set on '{key}'.")


@tags_group.command("list", help="List all tags for a secret key.")
@click.argument("key")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", default=None)
def list_cmd(key: str, vault: str, password: str | None) -> None:
    pw = password or _prompt_password(confirm=False)
    bucket = list_tags(vault, pw, key)
    if bucket:
        click.echo("  ".join(bucket))
    else:
        click.echo(f"No tags set for '{key}'.")


@tags_group.command("find", help="Find all secret keys that have a given tag.")
@click.argument("tag")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", default=None)
def find_cmd(tag: str, vault: str, password: str | None) -> None:
    pw = password or _prompt_password(confirm=False)
    keys = keys_for_tag(vault, pw, tag)
    if keys:
        for k in keys:
            click.echo(k)
    else:
        click.echo(f"No secrets tagged '{tag}'.")
