"""
Sync the Kart Medulla CN1-CN10 connector pinout from dv-hardware into kart-docs.

The pin assignments are only meaningful next to the schematic that defines them,
so dv-hardware owns the table and kart-docs republishes it. This script copies
`projects/kart-medulla/docs/pinout-cn-connectors.md` verbatim, prepending a
provenance banner and a hash of the source.

The result IS committed to kart-docs, unlike the wiring and BOM tables which are
rendered at build time by mkdocs hooks. GitHub Actions checks out kart-docs
alone, so a build-time hook could not reach dv-hardware; committing the copy
keeps the published site buildable from this repo by itself.

Usage:
    uv run python scripts/sync_pinout.py            # regenerate the page
    uv run python scripts/sync_pinout.py --check    # fail if the page is stale

`--check` exits 0 when dv-hardware is not checked out, so it is safe to run
anywhere; it can only report staleness when it can see the source.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_REL = "projects/kart-medulla/docs/pinout-cn-connectors.md"
OUTPUT = REPO_ROOT / "docs/assembly/electronics/kart-medulla/pinout.md"
SOURCE_URL = (
    "https://github.com/rubenayla/dv-hardware/blob/main/"
    "projects/kart-medulla/docs/pinout-cn-connectors.md"
)
HASH_PREFIX = "<!-- sync_pinout source-sha256: "


def default_source() -> Path:
    """Locate dv-hardware: $DV_HARDWARE if set, else a sibling of this repo."""
    root = os.environ.get("DV_HARDWARE")
    base = Path(root).expanduser() if root else REPO_ROOT.parent / "dv-hardware"
    return base / SOURCE_REL


def render(source_text: str) -> str:
    digest = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    banner = f"""{HASH_PREFIX}{digest} -->
!!! info "Generated page — edit it in `dv-hardware`, not here"
    This is a verbatim copy of [`{SOURCE_REL}`]({SOURCE_URL}) in the **dv-hardware**
    repo, which holds the KiCad schematic that defines these assignments. Changes
    made here are overwritten. To update: edit the file in dv-hardware, then run
    `uv run python scripts/sync_pinout.py` in kart-docs and commit the result.

    Related: [Kart Medulla board](index.md) · [whole-kart wire list](../wiring.md#wire-list-whole-kart)
    · ESP32-S3 GPIO map in dv-hardware's `pinout-esp32-s3.md`.

"""
    return banner + source_text.lstrip("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=None, help="path to pinout-cn-connectors.md")
    parser.add_argument("--check", action="store_true", help="verify the page is up to date")
    args = parser.parse_args()

    source = args.source or default_source()
    if not source.is_file():
        message = (
            f"dv-hardware source not found at {source}\n"
            "Set DV_HARDWARE=/path/to/dv-hardware or pass --source."
        )
        if args.check:
            print(f"skipped: {message}")
            return 0
        print(f"error: {message}", file=sys.stderr)
        return 1

    expected = render(source.read_text(encoding="utf-8"))
    current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else None

    if args.check:
        if current == expected:
            print(f"up to date: {OUTPUT.relative_to(REPO_ROOT)}")
            return 0
        print(
            f"STALE: {OUTPUT.relative_to(REPO_ROOT)} does not match {source}.\n"
            "Run: uv run python scripts/sync_pinout.py",
            file=sys.stderr,
        )
        return 1

    if current == expected:
        print(f"unchanged: {OUTPUT.relative_to(REPO_ROOT)}")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"wrote: {OUTPUT.relative_to(REPO_ROOT)} ({len(expected.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
