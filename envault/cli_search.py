"""CLI commands for searching secrets in the vault."""

from __future__ import annotations

import click

from envault.cli import _prompt_password
from envault.search import search_keys, search_values, format_results


@click.group(name="search")
def search_group() -> None:
    """Search secrets by key pattern or value substring."""


@search_group.command(name="keys")
@click.argument("pattern")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
@click.option("--show-values", is_flag=True, default=False, help="Reveal decrypted values.")
def keys_cmd(pattern: str, vault: str, show_values: bool) -> None:
    """Search secret keys matching PATTERN (glob, e.g. 'DB_*')."""
    password = _prompt_password(confirm=False)
    try:
        results = search_keys(vault, password, pattern, reveal_values=show_values)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    click.echo(format_results(results, reveal_values=show_values))
    if results:
        click.echo(f"\n{len(results)} match(es) found.", err=True)


@search_group.command(name="values")
@click.argument("substring")
@click.option("--vault", default=".envault", show_default=True, help="Vault file path.")
def values_cmd(substring: str, vault: str) -> None:
    """Search secrets whose values contain SUBSTRING."""
    password = _prompt_password(confirm=False)
    try:
        results = search_values(vault, password, substring)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    click.echo(format_results(results, reveal_values=True))
    if results:
        click.echo(f"\n{len(results)} match(es) found.", err=True)
