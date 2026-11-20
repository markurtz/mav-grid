# Copyright 2026 markurtz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command line interface for the MAV Grid toolkit.

Run it as ``mav-grid`` or ``python -m mav_grid``. Subcommands for schema
export, validation and generation are added as those subpackages land.
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from mav_grid.settings import get_settings
from mav_grid.spec import SPEC_NAME, SPEC_STATUS, SPEC_VERSION
from mav_grid.version import __version__

__all__ = ["COMPONENTS", "app", "main"]

COMPONENTS: tuple[tuple[str, str, str], ...] = (
    ("schema", "mav_grid.schema", "planned"),
    ("generators", "mav_grid.generators", "planned"),
    ("plates", "mav_grid.plates", "planned"),
    ("adapters", "mav_grid.adapters", "planned"),
    ("export", "mav_grid.export", "planned"),
)
"""Toolkit components as (name, module, status), shown by ``mav-grid info``."""

app = typer.Typer(
    help="MAV Grid: open parametric dovetail-groove grid and face-plate toolkit.",
    context_settings={"help_option_names": ["-h", "--help"]},
)


def main() -> None:
    """Run the CLI application."""
    app()


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            is_eager=True,
            help="Show the toolkit version and exit.",
        ),
    ] = None,
) -> None:
    """Global options for the MAV Grid CLI."""
    if version:
        typer.echo(f"mav-grid v{__version__}")
        raise typer.Exit
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit


@app.command()
def info() -> None:
    """Show the toolkit version, the targeted spec and component status."""
    console = Console()
    settings = get_settings()
    console.print(f"[bold]mav-grid[/bold] v{__version__}")
    console.print(f"{SPEC_NAME} {SPEC_VERSION} ({SPEC_STATUS})")
    console.print(f"Output directory: {settings.output_dir}")

    table = Table(title="Components")
    table.add_column("Component")
    table.add_column("Module")
    table.add_column("Status")
    for name, module, status in COMPONENTS:
        table.add_row(name, module, status)
    console.print(table)


if __name__ == "__main__":
    main()
