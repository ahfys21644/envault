"""CLI commands for diffing vault secrets against a .env file."""

import click

from envault.audit import record_event
from envault.cli import _prompt_password
from envault.diff import diff_vault_vs_file, format_diff


@click.group(name="diff")
def diff_group():
    """Compare vault secrets with a .env file."""


@diff_group.command(name="run")
@click.argument("dotenv_path", default=".env", metavar="DOTENV_FILE")
@click.option("--vault", "vault_path", default=".envault", show_default=True, help="Path to vault file.")
@click.option("--show-values", is_flag=True, default=False, help="Show changed values in output.")
@click.option("--only", type=click.Choice(["added", "removed", "changed", "unchanged"]), default=None, help="Filter by diff status.")
@click.pass_context
def run_cmd(ctx, dotenv_path: str, vault_path: str, show_values: bool, only):
    """Diff vault secrets against DOTENV_FILE (default: .env)."""
    password = _prompt_password(confirm=False)
    try:
        entries = diff_vault_vs_file(vault_path, dotenv_path, password)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except Exception as exc:
        raise click.ClickException(f"Diff failed: {exc}") from exc

    if only:
        entries = [e for e in entries if e.status == only]

    output = format_diff(entries, show_values=show_values)
    click.echo(output)

    counts = {"added": 0, "removed": 0, "changed": 0, "unchanged": 0}
    for e in entries:
        counts[e.status] += 1
    click.echo(
        f"\nSummary: {counts['added']} added, {counts['removed']} removed, "
        f"{counts['changed']} changed, {counts['unchanged']} unchanged."
    )

    record_event("diff", {"vault": vault_path, "dotenv": dotenv_path, "total": len(entries)})
