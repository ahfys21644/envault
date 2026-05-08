"""CLI commands for template rendering."""

from __future__ import annotations

from pathlib import Path

import click

from envault.cli import _prompt_password
from envault.template import render_template_file


@click.group(name="template", help="Render template files using vault secrets.")
def template_group() -> None:
    pass


@template_group.command(name="render", help="Render a template file, substituting {{ KEY }} placeholders.")
@click.argument("template_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("-o", "--output", "output_file", default=None, type=click.Path(dir_okay=False, path_type=Path), help="Write rendered output to this file instead of stdout.")
@click.option("--vault", "vault_file", default=".envault", show_default=True, type=click.Path(dir_okay=False, path_type=Path), help="Path to the vault file.")
@click.option("--strict", is_flag=True, default=False, help="Exit with error if any placeholders are missing.")
def render_cmd(
    template_file: Path,
    output_file: Path | None,
    vault_file: Path,
    strict: bool,
) -> None:
    password = _prompt_password(confirm=False)

    result = render_template_file(
        template_path=template_file,
        vault_path=vault_file,
        password=password,
        output_path=output_file,
    )

    if output_file is None:
        click.echo(result.output, nl=False)
    else:
        click.echo(f"Written to {output_file}")

    if result.substituted:
        click.echo(f"Substituted {len(result.substituted)} key(s): {', '.join(result.substituted)}", err=True)

    if result.missing:
        click.echo(f"Warning: {len(result.missing)} missing key(s): {', '.join(result.missing)}", err=True)
        if strict:
            raise click.ClickException("Aborting: unresolved placeholders in strict mode.")
