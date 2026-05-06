"""CLI commands for inspecting the envault audit log."""

from pathlib import Path
from typing import Optional

import click

from envault.audit import clear_log, read_events


@click.group("audit")
def audit_group():
    """Inspect and manage the audit log."""


@audit_group.command("log")
@click.option(
    "--limit",
    "-n",
    default=20,
    show_default=True,
    help="Number of recent entries to show.",
)
@click.option(
    "--vault",
    default=None,
    help="Filter entries by vault name.",
)
@click.option(
    "--action",
    default=None,
    type=click.Choice(["set", "get", "delete", "import", "export", "push", "pull"]),
    help="Filter entries by action type.",
)
def log_cmd(limit: int, vault: Optional[str], action: Optional[str]):
    """Display recent audit log entries."""
    events = read_events(limit=limit)
    if vault:
        events = [e for e in events if e.get("vault") == vault]
    if action:
        events = [e for e in events if e.get("action") == action]
    if not events:
        click.echo("No audit log entries found.")
        return
    for event in events:
        status = click.style("OK", fg="green") if event["success"] else click.style("FAIL", fg="red")
        key_part = f"  key={event['key']}" if event.get("key") else ""
        vault_part = f"  vault={event['vault']}" if event.get("vault") else ""
        click.echo(
            f"[{event['timestamp']}] {event['action'].upper():8s} {status}"
            f"{key_part}{vault_part}  user={event['user']}"
        )


@audit_group.command("clear")
@click.confirmation_option(prompt="This will permanently erase the audit log. Continue?")
def clear_cmd():
    """Erase all audit log entries."""
    clear_log()
    click.echo("Audit log cleared.")
