#!/usr/bin/env python3
"""Create a new part: a random ID, its doc page, and a QR encoding only that ID.

The QR contains ONLY the ID (e.g. ``1234567890123456``) — no domain, no org name, no URL.
Resolution is done by the scanner page at ``docs/scan.md``, which navigates relative to the
part page. This keeps every printed label permanent: renaming the GitHub org, letting a domain
lapse, or moving hosting never invalidates a label, because the label carries no external name.

An ID names a DESIGN REVISION, not an individual object: every unit built to the same revision gets
the same sticker and the same page. It is a part number, not a serial number — so run this once per
revision (``... v2`` is a new part), not once per board built. Rationale in history.md, 2026-07-31.

Design notes (full reasoning in ~/vault/inventory/history.md, 2026-06-13 addendum 7):
- ID = 16 random decimal digits (53.15 bits of entropy, log2(10**16)). The alphabet is exactly ``0-9``.
- Why all-digit: easiest to read and transcribe by hand (no ``0``/``O`` or ``1``/``l`` ambiguity,
  which is why we left base36 behind), and digits ride the QR's *numeric mode* (3.33 bits/digit,
  ~0% waste) — so the QR payload is actually SMALLER than base36-in-byte-mode despite the longer
  string, and it fits the smallest QR (Version 1, 21x21) even at ECC level H (max error recovery).
  All-digit is also the most standard form there is (GS1 trade/logistics codes are exactly this).
- 53.15 bits is plenty without any central list or duplicate check: ~1-in-160M collision at 10,000
  parts. The cheap exists() retry below is a safety net, not a real dependency.
- Still text-safe in every channel the ID flows through — QR payload, filename (``docs/p/<id>.md``),
  URL path (``/p/<id>/``), the string the JS QR reader returns, human typing. Digits are the safest
  possible subset (no case, no special chars), so raw bytes (NUL, non-UTF-8) are avoided for free.
- Display only: the ID is shown grouped in 4s (``1234 5678 9012 3456``) for readability, exactly like
  a credit card or IBAN. Those spaces are NEVER stored or encoded — not in the QR, filename, or URL —
  and are stripped on input. The canonical ID is always the bare 16 digits.

Usage:
    python scripts/new_part.py --title "Stepper motor NEMA 23" [--bom-id steering_motor] [--notes "..."]
"""

from __future__ import annotations

import argparse
import secrets
from pathlib import Path

import segno

REPO_ROOT = Path(__file__).resolve().parent.parent
PARTS_DIR = REPO_ROOT / "docs" / "p"
QR_DIR = PARTS_DIR / "qr"

ID_LEN = 16  # 16 decimal digits = 53.15 bits (log2(10**16)); collision negligible for thousands of parts


def make_id() -> str:
    """Return a random ID as a zero-padded 16-digit decimal string (bare, no spaces)."""
    return str(secrets.randbelow(10 ** ID_LEN)).rjust(ID_LEN, "0")


def grouped(pid: str) -> str:
    """Human-display form: digits in groups of 4. Display only — never stored or encoded."""
    return " ".join(pid[i:i + 4] for i in range(0, len(pid), 4))


PAGE_TEMPLATE = """\
---
title: {title}
part_id: {pid}
---

# {title}

**Part ID:** `{pid_grouped}`
{bom_line}
{notes_line}
<!-- Edit this page: link to a BOM component, add photos, specs, notes, history. -->
"""


def zpl_snippet(pid: str) -> str:
    """ZPL for the Zebra GK420t (203 dpi). UNTESTED until the printer arrives — validate on
    https://labelary.com (set 8 dpmm, label ~25x15mm) before trusting the layout.
    QR data is the bare ID; the printed human line is grouped in 4s for easy transcription."""
    return (
        "^XA\n"
        "^FO20,20^BQN,2,5^FDLA,{pid}^FS\n"
        "^FO20,170^A0N,22,22^FD{pid_grouped}^FS\n"
        "^XZ"
    ).format(pid=pid, pid_grouped=grouped(pid))


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
        PAGE_TEMPLATE.format(
            title=title, pid=pid, pid_grouped=grouped(pid), bom_line=bom_line, notes_line=notes_line
        )
    )

    qr_path = QR_DIR / f"{pid}.png"
    # make_qr (not make) forces a standard QR Code, never a Micro QR — Micro QR is not reliably
    # read by phone cameras or the html5-qrcode scanner. error="h": 16 digits in numeric mode still
    # fit Version 1 (21x21) at the highest error-correction level, so the label is as robust as
    # possible at no extra size.
    segno.make_qr(pid, error="h").save(str(qr_path), scale=8, border=4)

    print(f"Part ID : {pid}  ({grouped(pid)})")
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
