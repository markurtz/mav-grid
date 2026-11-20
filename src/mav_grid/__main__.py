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

Run it as ``mav-grid`` or ``python -m mav_grid``. The commands follow the
order of the work: ``spec`` reads and checks the specification files, ``new``
writes a claim record, ``validate`` checks one, and ``build`` turns records
into release folders.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.table import Table

from mav_grid.settings import get_settings
from mav_grid.spec import (
    HARDWARE_LICENCE,
    SCHEMA_ID_BASE,
    SPEC_NAME,
    SPEC_STATUS,
    SPEC_VERSION,
)
from mav_grid.version import __version__

__all__ = ["COMPONENTS", "app", "main"]

COMPONENTS: tuple[tuple[str, str, str], ...] = (
    ("schema", "mav_grid.schema", "experimental"),
    ("geometry", "mav_grid.geometry", "experimental"),
    ("generators", "mav_grid.generators", "experimental"),
    ("plates", "mav_grid.plates", "experimental"),
    ("adapters", "mav_grid.adapters", "experimental"),
    ("export", "mav_grid.export", "experimental"),
)
"""Toolkit components as (name, module, status), shown by ``mav-grid info``."""

app = typer.Typer(
    help="MAV Grid: open parametric dovetail-groove grid and face-plate toolkit.",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=False,
)
spec_app = typer.Typer(help="Read and check the specification files.")
new_app = typer.Typer(help="Write the claim record of a new part.")
app.add_typer(spec_app, name="spec")
app.add_typer(new_app, name="new")

console = Console()

SetOption = Annotated[
    list[str] | None,
    typer.Option(
        "--set",
        metavar="NAME=VALUE",
        help="Replace one constant of the parameter file. Repeatable. "
        "A part built this way is not MAV Grid conforming (rule K-3).",
    ),
]
ParamsOption = Annotated[
    Path | None,
    typer.Option("--params", help="Parameter file to use in place of the spec's."),
]
OutOption = Annotated[
    Path | None,
    typer.Option("--out", "-o", help="File to write. Printed when omitted."),
]
SizeOption = Annotated[str, typer.Option(help="Groove size: small or large.")]


def main() -> None:
    """Run the CLI application."""
    app()


def _params(path: Path | None = None, values: list[str] | None = None) -> Any:
    from mav_grid.schema import Params  # noqa: PLC0415

    params = Params.load(path)
    changes: dict[str, float] = {}
    for item in values or []:
        name, _, value = item.partition("=")
        try:
            changes[name.strip()] = float(value)
        except ValueError:
            raise typer.BadParameter(f"'{item}' is not NAME=NUMBER") from None
    try:
        return params.with_values(**changes) if changes else params
    except KeyError as error:
        raise typer.BadParameter(str(error.args[0])) from None


def _pair(text: str, what: str) -> tuple[int, int]:
    parts = text.lower().replace("x", ",").split(",")
    try:
        first, second = (int(part) for part in parts)
    except ValueError:
        raise typer.BadParameter(f"{what} '{text}' is not COLSxROWS") from None
    return first, second


def _emit(record: Any, out: Path | None) -> None:
    text = json.dumps(record.to_dict(), indent=2, ensure_ascii=False) + "\n"
    if out is None:
        typer.echo(text, nl=False)
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    typer.echo(f"wrote {out}")


def _made(make: Callable[[], Any]) -> Any:
    """Run a record builder and report a bad id or value as a usage error."""
    try:
        return make()
    except (KeyError, ValueError, NotImplementedError) as error:
        raise typer.BadParameter(str(error.args[0] if error.args else error)) from None


def _table(title: str, columns: list[str], rows: list[list[Any]]) -> None:
    table = Table(title=title)
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*(str(cell) for cell in row))
    console.print(table)


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
    from mav_grid.geometry.solid import kernel_available  # noqa: PLC0415

    settings = get_settings()
    console.print(f"[bold]mav-grid[/bold] v{__version__}")
    console.print(f"{SPEC_NAME} {SPEC_VERSION} ({SPEC_STATUS})")
    console.print(f"Schema id base: {SCHEMA_ID_BASE}")
    console.print(f"Hardware licence: {HARDWARE_LICENCE}")
    console.print(f"Output directory: {settings.output_dir}")
    kernel = (
        "installed" if kernel_available() else "missing (pip install mav-grid[cad])"
    )
    console.print(f"CAD kernel: {kernel}")
    _table(
        "Components", ["Component", "Module", "Status"], [list(c) for c in COMPONENTS]
    )


def _vectors() -> dict[str, Any]:
    from mav_grid import schema  # noqa: PLC0415

    return schema.build_vectors(
        schema.load_data("params"),
        schema.load_examples("valid"),
        schema.load_data("kinds"),
    )


def _vector_differences() -> list[str]:
    from mav_grid import schema  # noqa: PLC0415

    stored = schema.load_data("vectors")
    return schema.compare_vectors(stored, _vectors(), stored["tolerance"])


@spec_app.command("check")
def spec_check() -> None:
    """Check the schemas, data files, examples and test vectors of the spec."""
    from mav_grid import schema  # noqa: PLC0415
    from mav_grid.generators import check_record  # noqa: PLC0415

    problems = [*schema.check_schemas(), *schema.check_data()]
    for name, doc in schema.load_examples("valid").items():
        problems += [f"{name}: {i}" for i in check_record(doc) if i.severity == "error"]
    expected = schema.load_json(
        schema.spec_dir() / "examples" / "invalid" / "expected.json"
    )
    for name, doc in schema.load_examples("invalid").items():
        found = {i.rule for i in check_record(doc) if i.severity == "error"}
        entry = expected.get(name, {})
        wanted = set(entry.get("rules", [])) if entry.get("schema_valid") else set()
        if not found or not wanted <= found:
            problems.append(
                f"{name}: expected errors {sorted(wanted)}, got {sorted(found)}"
            )
    problems += _vector_differences()
    for line in problems:
        typer.echo(line, err=True)
    if problems:
        raise typer.Exit(1)
    typer.echo(f"{SPEC_NAME} {SPEC_VERSION}: schemas, data, examples and vectors agree")


@spec_app.command("derive")
def spec_derive(values: SetOption = None, params_file: ParamsOption = None) -> None:
    """Print the values that follow from the constants (rule C-9)."""
    from mav_grid.schema import derive  # noqa: PLC0415

    derived = derive(_params(params_file, values).raw)
    names = list(derived["small"])
    rows = [
        [n, f"{derived['small'][n]:.4f}", f"{derived['large'][n]:.4f}"] for n in names
    ]
    _table("Derived values, mm and degrees", ["Value", "Small", "Large"], rows)


@spec_app.command("vectors")
def spec_vectors(
    write: Annotated[
        bool, typer.Option(help="Rewrite spec/data/vectors.json.")
    ] = False,
) -> None:
    """Recompute the test vectors of Annex A and compare or rewrite the file."""
    from mav_grid import schema  # noqa: PLC0415

    actual = _vectors()
    path = schema.spec_dir() / "data" / "vectors.json"
    if write:
        text = json.dumps(actual, indent=2, ensure_ascii=False) + "\n"
        path.write_text(text, encoding="utf-8")
        typer.echo(f"wrote {path}")
        return
    differences = _vector_differences()
    for line in differences:
        typer.echo(line, err=True)
    if differences:
        raise typer.Exit(1)
    typer.echo("vectors agree with the constants")


@spec_app.command("kinds")
def spec_kinds() -> None:
    """List the plate kinds and what the generator draws for each."""
    from mav_grid.plates import kind_table  # noqa: PLC0415

    rows = [
        [
            k["id"],
            k["name"],
            k["min_span"]["small"],
            k["min_span"]["large"],
            k["status"],
        ]
        for k in kind_table()
    ]
    _table("Plate kinds", ["Id", "Name", "Min span S", "Min span L", "Generator"], rows)


@spec_app.command("adapters")
def spec_adapters(
    drawn: Annotated[bool, typer.Option(help="Only systems with a generator.")] = False,
) -> None:
    """List the other systems of the support register and the adapters drawn."""
    from mav_grid.adapters import adapter_table  # noqa: PLC0415

    rows = [
        [a["id"], a["family"], a["level"], "yes" if a["drawn"] else ""]
        for a in adapter_table()
        if a["drawn"] or not drawn
    ]
    _table("Other systems", ["Id", "Family", "Support level", "Drawn"], rows)


@spec_app.command("decisions")
def spec_decisions(
    proposed: Annotated[
        bool, typer.Option(help="Only the open draft choices.")
    ] = False,
) -> None:
    """List the decisions behind the spec and the choices still proposed."""
    from mav_grid.schema import load_data  # noqa: PLC0415

    rows = [
        [d["id"], d.get("by", ""), d["title"], d.get("answer", "")]
        for d in load_data("decisions")["decisions"]
        if not proposed or d.get("by") != "owner"
    ]
    _table("Decisions", ["Id", "By", "Title", "Answer"], rows)
    names = ", ".join(_params().proposed())
    console.print(f"Constants and limits tagged proposed: {names}")


@app.command()
def validate(
    files: Annotated[
        list[Path],
        typer.Argument(exists=True, dir_okay=False, help="Claim record files."),
    ],
    values: SetOption = None,
    params_file: ParamsOption = None,
) -> None:
    """Check claim records against the schema and the rules of the spec."""
    from mav_grid.generators import check_record  # noqa: PLC0415
    from mav_grid.schema import load_json  # noqa: PLC0415

    params = _params(params_file, values)
    failed = False
    for path in files:
        issues = check_record(load_json(path), params)
        errors = [issue for issue in issues if issue.severity == "error"]
        failed = failed or bool(errors)
        typer.echo(f"{path}: {'FAIL' if errors else 'ok'}")
        for issue in issues:
            typer.echo(f"  {issue}")
    if failed:
        raise typer.Exit(1)


@app.command()
def claim(
    file: Annotated[
        Path, typer.Argument(exists=True, dir_okay=False, help="A claim record file.")
    ],
) -> None:
    """Print the claim line a record derives (rule K-2)."""
    from mav_grid.schema import claim_line, load_json  # noqa: PLC0415

    typer.echo(claim_line(load_json(file)))


@app.command()
def build(
    files: Annotated[
        list[Path],
        typer.Argument(exists=True, dir_okay=False, help="Claim record files."),
    ],
    out: Annotated[
        Path | None,
        typer.Option("--out", "-o", help="Folder that gets one folder per record."),
    ] = None,
    formats: Annotated[
        list[str] | None,
        typer.Option(
            "--format",
            "-f",
            help="step, stl, 3mf, glb, preview, svg or dxf. Repeatable. All by "
            "default, or svg and dxf when the CAD kernel is not installed.",
        ),
    ] = None,
    values: SetOption = None,
    params_file: ParamsOption = None,
) -> None:
    """Build claim records into release folders of geometry and records."""
    from mav_grid.export import FORMATS, SOLID_FORMATS, write_release  # noqa: PLC0415
    from mav_grid.generators import RecordError, load_record, plan_record  # noqa: PLC0415
    from mav_grid.geometry.solid import (  # noqa: PLC0415
        KernelMissingError,
        kernel_available,
    )

    params = _params(params_file, values)
    settings = get_settings()
    root = out or settings.project_root / settings.output_dir
    wanted = formats or [
        name for name in FORMATS if kernel_available() or name not in SOLID_FORMATS
    ]
    for path in files:
        try:
            record = load_record(path)
        except RecordError as error:
            for line in error.problems:
                typer.echo(f"{path}: {line}", err=True)
            raise typer.Exit(1) from None
        try:
            plan = plan_record(record, params=params)
        except NotImplementedError as error:
            typer.echo(f"{path}: {error}", err=True)
            raise typer.Exit(1) from None
        try:
            release = write_release(
                plan, root / path.stem, formats=wanted, params=params
            )
        except KernelMissingError as error:
            typer.echo(str(error), err=True)
            raise typer.Exit(1) from None
        typer.echo(f"{path.name}: {len(release.files)} files in {release.folder}")
        for note in release.report.get("notes", []):
            typer.echo(f"  note: {note}")


def _face_options(size: str, mode: str, span: str, kind: str) -> dict[str, Any]:
    return {
        "size": size,
        "build_mode": mode,
        "span": _pair(span, "span"),
        "kind": kind,
    }


ModeOption = Annotated[
    str,
    typer.Option(
        "--mode",
        help="routed-integral, swap-base, cut-down-sites or surface-plates.",
    ),
]
SpanOption = Annotated[str, typer.Option(help="Plate span, COLSxROWS.")]
KindOption = Annotated[str, typer.Option(help="Plate kind id (see spec kinds).")]


@new_app.command("panel")
def new_panel(  # noqa: PLR0917
    cells: Annotated[str, typer.Argument(help="Face size, COLSxROWS.")],
    size: SizeOption = "small",
    mode: ModeOption = "swap-base",
    span: SpanOption = "1x1",
    kind: KindOption = "plain",
    out: OutOption = None,
) -> None:
    """Write the record of a flat panel with one face."""
    from mav_grid.generators import panel  # noqa: PLC0415

    cols, rows = _pair(cells, "cells")
    _emit(
        _made(lambda: panel(cols, rows, **_face_options(size, mode, span, kind))), out
    )


@new_app.command("corner")
def new_corner(  # noqa: PLR0917
    cells: Annotated[str, typer.Argument(help="Size of each face, COLSxROWS.")],
    angle: Annotated[float, typer.Option(help="Fold angle on the grid side.")] = 270.0,
    size: SizeOption = "small",
    mode: ModeOption = "swap-base",
    span: SpanOption = "1x1",
    kind: KindOption = "plain",
    out: OutOption = None,
) -> None:
    """Write the record of two faces that meet at a fold."""
    from mav_grid.generators import corner  # noqa: PLC0415

    cols, rows = _pair(cells, "cells")
    options = _face_options(size, mode, span, kind)
    record = _made(lambda: corner(cols, cols, rows, angle, **options))
    _emit(record, out)


@new_app.command("column")
def new_column(  # noqa: PLR0917
    cells: Annotated[str, typer.Argument(help="Size of each side, COLSxROWS.")],
    sides: Annotated[int, typer.Option(help="Number of sides.")] = 6,
    size: SizeOption = "small",
    mode: ModeOption = "swap-base",
    span: SpanOption = "1x1",
    kind: KindOption = "plain",
    out: OutOption = None,
) -> None:
    """Write the record of a column: a ring of faces that look outward."""
    from mav_grid.generators import column  # noqa: PLC0415

    cols, rows = _pair(cells, "cells")
    _emit(
        _made(
            lambda: column(sides, cols, rows, **_face_options(size, mode, span, kind))
        ),
        out,
    )


@new_app.command("box")
def new_box(  # noqa: PLR0917
    cells: Annotated[str, typer.Argument(help="Outside size, COLSxROWSxLAYERS.")],
    size: SizeOption = "small",
    mode: ModeOption = "swap-base",
    span: SpanOption = "1x1",
    kind: KindOption = "plain",
    out: OutOption = None,
) -> None:
    """Write the record of a box whose grids face outward."""
    from mav_grid.generators import box  # noqa: PLC0415

    try:
        cols, rows, layers = (int(part) for part in cells.lower().split("x"))
    except ValueError:
        raise typer.BadParameter(f"'{cells}' is not COLSxROWSxLAYERS") from None
    _emit(
        _made(lambda: box(cols, rows, layers, **_face_options(size, mode, span, kind))),
        out,
    )


@new_app.command("plate")
def new_plate(
    span: Annotated[str, typer.Argument(help="Plate span, COLSxROWS.")] = "1x1",
    size: SizeOption = "small",
    kind: KindOption = "plain",
    process: Annotated[str, typer.Option(help="How the plate is made.")] = "printed",
    out: OutOption = None,
) -> None:
    """Write the record of a loose face plate."""
    from mav_grid.generators import plate_record  # noqa: PLC0415

    cells = _pair(span, "span")
    record = _made(
        lambda: plate_record(size=size, span=cells, kind=kind, process=process)
    )
    _emit(record, out)


@new_app.command("key")
def new_key(
    reference: Annotated[str, typer.Argument(help="Reference key id of the spec.")],
    out: OutOption = None,
) -> None:
    """Write the record of one of the spec's reference keys."""
    from mav_grid.generators import key_record  # noqa: PLC0415

    _emit(_made(lambda: key_record(reference)), out)


@new_app.command("gauge")
def new_gauge(
    gauge: Annotated[str, typer.Argument(help="Gauge id, G-1 to G-4.")],
    out: OutOption = None,
) -> None:
    """Write the record of a gauge."""
    from mav_grid.generators import gauge_record  # noqa: PLC0415

    _emit(_made(lambda: gauge_record(gauge)), out)


@new_app.command("adapter")
def new_adapter(
    system: Annotated[str, typer.Argument(help="System id (see spec adapters).")],
    out: OutOption = None,
) -> None:
    """Write the record of an adapter to another system."""
    from mav_grid.adapters import adapter_record  # noqa: PLC0415

    _emit(_made(lambda: adapter_record(system)), out)


if __name__ == "__main__":
    main()
