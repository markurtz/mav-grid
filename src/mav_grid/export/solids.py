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

"""Write built solids to STEP, STL, 3MF and GLB, and a line-drawing preview.

These writers need the optional ``cad`` extra, like the kernel module.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mav_grid.geometry.solid import BuiltAssembly, BuiltPart, kernel

__all__ = ["write_3mf", "write_glb", "write_preview", "write_step", "write_stl"]

VIEW_DIRECTION = (-1.0, -1.6, 1.1)
"""Where the preview camera sits, as a direction from the part's centre."""


def write_step(
    assembly: BuiltAssembly, path: Path | str, *, reference: bool = True
) -> Path:
    """Write every part of an assembly to one STEP file, each part labelled."""
    target = Path(path)
    kernel().export_step(assembly.compound(reference=reference), str(target))
    return target


def write_stl(part: BuiltPart, path: Path | str) -> Path:
    """Write one part as a binary STL mesh."""
    target = Path(path)
    kernel().export_stl(part.shape, str(target))
    return target


def write_3mf(part: BuiltPart, path: Path | str) -> Path:
    """Write one part as a 3MF mesh, in millimetres."""
    bd = kernel()
    target = Path(path)
    mesher = bd.Mesher(unit=bd.Unit.MM)
    mesher.add_shape(part.shape)
    mesher.write(str(target))
    return target


def write_glb(
    assembly: BuiltAssembly, path: Path | str, *, reference: bool = True
) -> Path:
    """Write an assembly as binary glTF, for viewers."""
    target = Path(path)
    kernel().export_gltf(
        assembly.compound(reference=reference), str(target), binary=True
    )
    return target


def _span(shape: Any) -> tuple[Any, float]:
    box = shape.bounding_box()
    return box.center(), max(box.size.X, box.size.Y, box.size.Z)


def write_preview(
    assembly: BuiltAssembly,
    path: Path | str,
    *,
    reference: bool = True,
    width: float = 160.0,
) -> Path:
    """Write a hidden-line view of an assembly as SVG.

    :param assembly: The built assembly.
    :param path: File to write.
    :param reference: Include reference parts.
    :param width: Rough width of the drawing in millimetres.
    :returns: The path written.
    """
    bd = kernel()
    shape = assembly.compound(reference=reference)
    centre, size = _span(shape)
    camera = centre + bd.Vector(*VIEW_DIRECTION).normalized() * (size * 4 + 100)
    visible, hidden = shape.project_to_viewport(
        tuple(camera), viewport_up=(0, 0, 1), look_at=tuple(centre)
    )
    exporter = bd.ExportSVG(scale=width / max(size, 1.0) / 1.6, margin=4)
    exporter.add_layer("hidden", line_color="darkgray", line_weight=0.15)
    exporter.add_layer("visible", line_color="black", line_weight=0.3)
    if hidden:
        exporter.add_shape(hidden, layer="hidden")
    exporter.add_shape(visible, layer="visible")
    target = Path(path)
    exporter.write(str(target))
    return target
