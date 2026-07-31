---
title: Parts (by ID)
---

# Parts (by ID)

A part carries a small QR sticker holding a short random ID. Scanning it with the
[Scan a part QR](../scan.md) page opens that part's page here, at `/p/<id>/`.

**An ID names a design revision, not an individual object.** Every unit built to the same revision
carries the same sticker and resolves to the same page — the ID is a *part number*, not a serial
number. Two revisions that look physically identical (an adapter board v1 and v2, say) get different
IDs and different pages, which is what the labels exist to disambiguate.

These pages are reached by **scanning or direct URL**, not from the sidebar — there is one per
labelled part and they are intentionally kept out of the navigation.

## How it works

- The QR encodes **only the ID** — no domain, no organisation name, no URL. That is what makes a
  printed label permanent: renaming the GitHub org, changing the domain, or moving hosting never
  invalidates a sticker, because the sticker carries no external name.
- The [scanner page](../scan.md) decodes the ID and navigates **relative** to itself, so the whole
  system can be rehosted anywhere without reprinting anything.

## Add a new part

```bash
python scripts/new_part.py --title "Stepper motor NEMA 23"
```

This generates the ID, creates `docs/p/<id>.md`, writes a QR PNG under `docs/p/qr/`, and prints a
ZPL snippet for the label printer.
