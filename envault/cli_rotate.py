"""CLI command group for key rotation."""

from __future__ import annotations

import click

from envault.cli import _prompt_password
from envault.rotate import rotate_key


@click.group("rotate")
def rotate_group() -> None:
    """Commands for rotating the vault encryption key."""


@rotate_group.command("run")
@click.option(
    "--vault",
    "vault_path",
    default=".envault",
    show_default=True,
    help="Path to the vault file.",
)
@click.option(
    "--old-password",
    default=None,
    help="Current vault password (prompted if omitted).",
)
@click.option(
    "--new-password",
    default=None,
    help="New vault password (prompted if omitted).",
)
def run_cmd(
    vault_path: str,
    old_password: str | None,
    new_password: str | None,
) -> None:
    """Re-encrypt all secrets in the vault with a new password."""
    if old_password is None:
        old_password = _prompt_password("Current password")
    if new_password is None:
        new_password = _prompt_password("New password")
        confirm = _prompt_password("Confirm new password")
        if new_password != confirm:
            raise click.ClickException("Passwords do not match.")

    try:
        result = rotate_key(vault_path, old_password, new_password)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    click.echo(
        f"Key rotation complete — "
        f"{result['rotated']} secret(s) re-encrypted, "
        f"{result['skipped']} skipped."
    )
    if result["skipped"]:
        click.echo(
            click.style(
                "Warning: some secrets could not be decrypted and were left unchanged.",
                fg="yellow",
            )
        )
