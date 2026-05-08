"""CLI commands for profile management."""

from __future__ import annotations

import click
from pathlib import Path

from envault.profile import (
    create_profile,
    delete_profile,
    assign_key,
    unassign_key,
    list_profiles,
    get_profile_keys,
)


@click.group(name="profile")
def profile_group():
    """Manage named profiles (environment sets)."""


@profile_group.command(name="create")
@click.argument("profile")
@click.option("--vault", default="vault.enc", show_default=True)
def create_cmd(profile: str, vault: str):
    """Create a new empty profile."""
    result = create_profile(Path(vault), profile)
    color = "green" if result.ok else "red"
    click.echo(click.style(result.message, fg=color))


@profile_group.command(name="delete")
@click.argument("profile")
@click.option("--vault", default="vault.enc", show_default=True)
def delete_cmd(profile: str, vault: str):
    """Delete an existing profile."""
    result = delete_profile(Path(vault), profile)
    color = "green" if result.ok else "red"
    click.echo(click.style(result.message, fg=color))


@profile_group.command(name="assign")
@click.argument("profile")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def assign_cmd(profile: str, key: str, vault: str):
    """Assign a key to a profile."""
    result = assign_key(Path(vault), profile, key)
    color = "green" if result.ok else "red"
    click.echo(click.style(result.message, fg=color))


@profile_group.command(name="unassign")
@click.argument("profile")
@click.argument("key")
@click.option("--vault", default="vault.enc", show_default=True)
def unassign_cmd(profile: str, key: str, vault: str):
    """Remove a key from a profile."""
    result = unassign_key(Path(vault), profile, key)
    color = "green" if result.ok else "red"
    click.echo(click.style(result.message, fg=color))


@profile_group.command(name="list")
@click.option("--vault", default="vault.enc", show_default=True)
def list_cmd(vault: str):
    """List all profiles and their keys."""
    profiles = list_profiles(Path(vault))
    if not profiles:
        click.echo("No profiles defined.")
        return
    for name, keys in profiles.items():
        key_str = ", ".join(keys) if keys else "(empty)"
        click.echo(f"  {name}: {key_str}")


@profile_group.command(name="show")
@click.argument("profile")
@click.option("--vault", default="vault.enc", show_default=True)
def show_cmd(profile: str, vault: str):
    """Show keys assigned to a profile."""
    keys = get_profile_keys(Path(vault), profile)
    if keys is None:
        click.echo(click.style(f"Profile '{profile}' not found.", fg="red"))
        return
    if not keys:
        click.echo(f"Profile '{profile}' has no keys assigned.")
        return
    for k in keys:
        click.echo(f"  {k}")
