"""CLI commands for the watch feature."""

from __future__ import annotations

from pathlib import Path

import click

from envault.cli import _prompt_password
from envault.watch import watch_file


@click.group("watch")
def watch_group() -> None:
    """Watch a .env file and auto-sync changes into the vault."""


@watch_group.command("start")
@click.argument("dotenv_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--vault",
    "vault_path",
    default="vault.json",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Path to the vault file.",
)
@click.option(
    "--interval",
    default=2.0,
    show_default=True,
    type=float,
    help="Poll interval in seconds.",
)
def start_cmd(dotenv_file: Path, vault_path: Path, interval: float) -> None:
    """Watch DOTENV_FILE and import changes into the vault on every save."""
    password = _prompt_password(confirm=False)

    click.echo(
        f"Watching {dotenv_file} (interval={interval}s). Press Ctrl+C to stop."
    )

    def _on_change(state):
        click.echo(
            f"  [sync #{state.changes_detected}] Imported secrets from {dotenv_file}"
        )

    state = watch_file(
        dotenv_path=dotenv_file,
        vault_path=vault_path,
        password=password,
        interval=interval,
        on_change=_on_change,
    )

    if state.errors:
        for err in state.errors:
            click.echo(f"  [error] {err}", err=True)

    click.echo(
        f"Stopped. Total syncs: {state.changes_detected}, errors: {len(state.errors)}."
    )
