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

"""Change the schema address or the licence expression in every file at once.

Two strings of the 0.11 draft are assumptions that wait for confirmation
(decision D-23): the base address of the schema ``$id`` values and the SPDX
expression of the hardware licence. Both appear in the schemas, the data
files, the examples, the samples and ``src/mav_grid/spec.py``. This script
replaces the current value, read from ``mav_grid.spec``, with a new one in
all of them.

Usage::

    python scripts/set_spec_identity.py --schema-base https://example.org/schema
    python scripts/set_spec_identity.py --licence "SHL-2.0"
    python scripts/set_spec_identity.py --schema-base ... --dry-run

Afterwards run ``mav-grid spec check`` and the tests.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mav_grid.spec import HARDWARE_LICENCE, SCHEMA_ID_BASE

ROOT = Path(__file__).resolve().parents[1]
TARGETS = ("spec", "samples", "src/mav_grid/spec.py", "docs", "README.md")
SUFFIXES = {".json", ".md", ".py"}


def _files() -> list[Path]:
    found: list[Path] = []
    for target in TARGETS:
        path = ROOT / target
        if path.is_file():
            found.append(path)
        elif path.is_dir():
            found += [p for p in sorted(path.rglob("*")) if p.suffix in SUFFIXES]
    return found


def replace_everywhere(pairs: list[tuple[str, str]], *, dry_run: bool) -> int:
    """Replace each old string with its new one and return the files changed.

    :param pairs: (old, new) strings.
    :param dry_run: Report only.
    :returns: Number of files that hold an old string.
    """
    changed = 0
    for path in _files():
        text = path.read_text(encoding="utf-8")
        new_text = text
        for old, new in pairs:
            new_text = new_text.replace(old, new)
        if new_text == text:
            continue
        changed += 1
        verb = "would change" if dry_run else "changed"
        print(f"[INFO] {verb} {path.relative_to(ROOT)}")
        if not dry_run:
            path.write_text(new_text, encoding="utf-8")
    return changed


def main() -> int:
    """Parse the arguments and run the replacement."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--schema-base", help=f"New base. Now: {SCHEMA_ID_BASE}")
    parser.add_argument("--licence", help=f"New expression. Now: {HARDWARE_LICENCE}")
    parser.add_argument("--dry-run", action="store_true", help="Change nothing.")
    args = parser.parse_args()
    pairs = []
    if args.schema_base:
        pairs.append((SCHEMA_ID_BASE, args.schema_base.rstrip("/")))
    if args.licence:
        pairs.append((HARDWARE_LICENCE, args.licence))
    if not pairs:
        parser.error("give --schema-base, --licence or both")
    changed = replace_everywhere(pairs, dry_run=args.dry_run)
    print(f"[INFO] {changed} files {'would change' if args.dry_run else 'changed'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
