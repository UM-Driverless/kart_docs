#!/usr/bin/env python3
"""Completeness + consistency checker for the wiring netlist (wiring.yaml).

Answers "is the wire list complete?" with a runnable command instead of a promise.

Checks:
  ERROR  phantom pin   - a net references a pin that no device declares
  ERROR  dangling net  - a net connects fewer than 2 pins (unless `single: true`)
  GAP    unwired pin   - a declared device pin is on no net and not in `no_connect`

Exit code: non-zero on ERRORs. GAPs are reported but do not fail unless --strict.

Usage:
  uv run python scripts/check_wiring.py [path/to/wiring.yaml] [--strict]
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

DEFAULT = Path(__file__).resolve().parent.parent / "docs/assembly/electronics/wiring/wiring.yaml"


def load(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def check(data: dict) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []
    gaps: list[str] = []

    devices = data.get("devices", {}) or {}
    nets = data.get("nets", []) or []
    no_connect = set(data.get("no_connect", []) or [])

    declared: set[str] = set()
    for dev, spec in devices.items():
        for pin in (spec or {}).get("pins", []) or []:
            declared.add(f"{dev}.{pin}")

    used: set[str] = set()
    seen_names: set[str] = set()
    pin_nets: dict[str, list[str]] = {}
    for net in nets:
        name = net.get("name", "<unnamed>")
        if name in seen_names:
            errors.append(f"duplicate net name: {name}")
        seen_names.add(name)
        pins = net.get("pins", []) or []
        for p in pins:
            if p not in declared:
                errors.append(f"phantom pin '{p}' in net '{name}' (no device declares it)")
            used.add(p)
            pin_nets.setdefault(p, []).append(name)
        if len(pins) < 2 and not net.get("single"):
            errors.append(f"dangling net '{name}': connects {len(pins)} pin(s), needs >= 2 (or `single: true`)")

    # a pin on more than one net is an accidental short (or the nets should be merged)
    for p, ns in sorted(pin_nets.items()):
        if len(ns) > 1:
            errors.append(f"pin '{p}' is on {len(ns)} nets ({', '.join(ns)}) — accidental short, or merge the nets")

    # no_connect entries must be real declared pins
    for p in sorted(no_connect - declared):
        errors.append(f"no_connect pin '{p}' is not declared by any device")

    for p in sorted(declared - used - no_connect):
        gaps.append(p)

    summary = {
        "devices": len(devices),
        "pins": len(declared),
        "nets": len(nets),
        "connectable": len(declared - no_connect),
        "no_connect": len(no_connect & declared),
        "wired": len(declared & used),
        "gaps": len(gaps),
    }
    return errors, gaps, summary


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    strict = "--strict" in sys.argv
    path = Path(args[0]) if args else DEFAULT

    data = load(path)
    errors, gaps, s = check(data)

    print(f"wiring netlist: {path}")
    print(f"  {s['devices']} devices, {s['pins']} pins, {s['nets']} nets")
    cov = (100 * s["wired"] / s["connectable"]) if s["connectable"] else 100
    print(
        f"  coverage: {s['wired']}/{s['connectable']} connectable pins wired "
        f"({cov:.0f}%); {s['no_connect']} no-connect"
    )

    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")

    if gaps:
        print(f"\nGAPS — declared pins not yet on any net ({len(gaps)}):")
        for g in gaps:
            print(f"  • {g}")

    if not errors and not gaps:
        print("\n✓ complete: every declared pin is wired, no dangling or phantom nets.")

    if errors:
        return 1
    if gaps and strict:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
