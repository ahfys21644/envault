"""CLI commands for renaming vault keys."""

from __future__ import annotations

import click

from envault.cli import _prompt_password
from envault.rename import rename_key


@click.group("rename", help="Rename keys inside the vault.")
def rename_group() -> None:  # pragma: no cover
    pass


@rename_group.command("run", help="Rename OLD_KEY to NEW_KEY inside the vault.")
@click.argument("old_key")
@click.argument("new_key")
@click.option(
    "--vault",
    "vault_path",
    default=".envault",
    show_default=True,
    help="Path to the vault file.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite NEW_KEY if it already exists.",
)
def run_cmd(old_key: str, new_key: str, vault_path: str, overwrite: bool) -> None:
    password = _prompt_password(confirm=False)
    result = rename_key(
        vault_path=vault_path,
        old_key=old_key,
        new_key=new_key,
        password=password,
        overwrite=overwrite,
    )
    if result.success:
        click.echo(result.message)
    else:
        click.echo(f"Error: {result.message}", err=True)
        raise SystemExit(1)
