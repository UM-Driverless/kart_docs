#!/usr/bin/env python3
"""Create a new part: a random ID, its doc page, and a QR encoding only that ID.

The QR contains ONLY the ID (e.g. ``a7f3k9qm2xp4d``) — no domain, no org name, no URL.
Resolution is done by the scanner page at ``docs/scan.md``, which navigates relative to the
part page. This keeps every printed label permanent: renaming the GitHub org, letting a domain
lapse, or moving hosting never invalidates a label, because the label carries no external name.

Design notes (full reasoning in ~/vault/inventory/history.md, 2026-06-13):
- ID = 64 random bits in base36 (lowercase + digits, 13 chars). Base36 (not base62) so IDs are
  safe as filenames on case-insensitive filesystems (macOS default). 64 bits = UUID-grade:
  collision is negligible without any central list or duplicate check.

Usage:
    python scripts/new_part.py --title "Stepper motor NEMA 23" [--bom-id steering_motor] [--notes "..."]
"""

from __future__ import annotations

import argparse
import secrets
import string
from pathlib import Path

import segno

REPO_ROOT = Path(__file__).resolve().parent.parent
PARTS_DIR = REPO_ROOT / "docs" / "p"
QR_DIR = PARTS_DIR / "qr"

_BASE36 = string.digits + string.ascii_lowercase  # 0-9a-z
ID_LEN = 13  # ceil(64 / log2(36)) = 13 chars covers the full 64-bit range


def make_id() -> str:
    """Return a 64-bit random ID encoded as a zero-padded 13-char base36 string."""
    n = secrets.randbits(64)
    if n == 0:
        return _BASE36[0] * ID_LEN
    chars = []
    while n:
        n, rem = divmod(n, 36)
        chars.append(_BASE36[rem])
    return "".join(reversed(chars)).rjust(ID_LEN, "0")


PAGE_TEMPLATE = """\
---
title: {title}
part_id: {pid}
---

# {title}

**Part ID:** `{pid}`
{bom_line}
{notes_line}
<!-- Edit this page: link to a BOM component, add photos, specs, notes, history. -->
"""


def zpl_snippet(pid: str) -> str:
    """ZPL for the Zebra GK420t (203 dpi). UNTESTED until the printer arrives — validate on
    https://labelary.com (set 8 dpmm, label ~25x15mm) before trusting the layout."""
    return (
        "^XA\n"
        "^FO20,20^BQN,2,5^FDLA,{pid}^FS\n"
        "^FO20,170^A0N,22,22^FD{pid}^FS\n"
        "^XZ"
    ).format(pid=pid)


def create_part(title: str, bom_id: str | None, notes: str | None) -> str:
    PARTS_DIR.mkdir(parents=True, exist_ok=True)
    QR_DIR.mkdir(parents=True, exist_ok=True)

    pid = make_id()
    page_path = PARTS_DIR / f"{pid}.md"
    while page_path.exists():  # astronomically unlikely; cheap safety net
        pid = make_id()
        page_path = PARTS_DIR / f"{pid}.md"

    bom_line = f"\n**BOM component:** `{bom_id}`\n" if bom_id else ""
    notes_line = f"\n{notes}\n" if notes else ""
    page_path.write_text(
        PAGE_TEMPLATE.format(title=title, pid=pid, bom_line=bom_line, notes_line=notes_line)
    )

    qr_path = QR_DIR / f"{pid}.png"
    # make_qr (not make) forces a standard QR Code, never a Micro QR — Micro QR is not reliably
    # read by phone cameras or the html5-qrcode scanner.
    segno.make_qr(pid, error="m").save(str(qr_path), scale=8, border=4)

    print(f"Part ID : {pid}")
    print(f"Page    : {page_path.relative_to(REPO_ROOT)}")
    print(f"QR PNG  : {qr_path.relative_to(REPO_ROOT)}")
    print(f"URL     : /p/{pid}/")
    print("\nZPL (validate on labelary.com before printing):")
    print(zpl_snippet(pid))
    return pid


def main() -> None:
    ap = argparse.ArgumentParser(description="Create a new part page + QR (ID-only).")
    ap.add_argument("--title", required=True, help="Human-readable part name")
    ap.add_argument("--bom-id", default=None, help="Optional BOM component id to link")
    ap.add_argument("--notes", default=None, help="Optional notes line for the page body")
    args = ap.parse_args()
    create_part(args.title, args.bom_id, args.notes)


if __name__ == "__main__":
    main()
