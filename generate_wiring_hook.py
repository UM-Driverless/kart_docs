"""
MkDocs hook that renders the wiring netlist (wiring.yaml) into a net-centric
table on the Wiring page, replacing the `<!-- WIRING_TABLE -->` marker.

Source of truth is docs/assembly/electronics/wiring/wiring.yaml — edit there,
never the generated table. Completeness is checked by scripts/check_wiring.py.
"""

from pathlib import Path

import yaml

WIRING_PAGE = "assembly/electronics/wiring.md"
YAML_REL = "assembly/electronics/wiring/wiring.yaml"
MARKER = "<!-- WIRING_TABLE -->"


def net_color(net: dict, color_code: dict) -> str:
    if net.get("color"):
        return net["color"]
    if net.get("class") == "power":
        return color_code.get(net.get("voltage", ""), "—")
    return color_code.get("signal", "white/gray")


def render_table(data: dict) -> str:
    color_code = data.get("color_code", {}) or {}
    nets = data.get("nets", []) or []

    lines = [
        "| Net | System | V | Colour | Connected pins | Notes |",
        "|---|---|---|---|---|---|",
    ]
    for net in nets:
        name = net.get("name", "—")
        status = net.get("status")
        if status:
            name = f"{name} *({status})*"
        v = net.get("voltage", "—")
        colour = net_color(net, color_code)
        pins = "<br>".join(f"`{p}`" for p in net.get("pins", []))
        note = net.get("note", "")
        lines.append(
            f"| **{name}** | {net.get('system', '—')} | {v} | {colour} | {pins} | {note} |"
        )

    # coverage footer
    declared = {
        f"{dev}.{pin}"
        for dev, spec in (data.get("devices", {}) or {}).items()
        for pin in (spec or {}).get("pins", []) or []
    }
    used = {p for net in nets for p in net.get("pins", [])}
    no_connect = set(data.get("no_connect", []) or [])
    gaps = sorted(declared - used - no_connect)
    cov = 100 * len(declared & used) // len(declared) if declared else 100

    footer = [
        "",
        f"*{len(nets)} nets over {len(declared)} declared pins — {cov}% wired. "
        "Generated from `wiring/wiring.yaml`; run `uv run python scripts/check_wiring.py` to re-check completeness.*",
    ]
    if gaps:
        footer.append("")
        footer.append(
            "**Unwired pins (gaps to close):** " + ", ".join(f"`{g}`" for g in gaps) + "."
        )
    return "\n".join(lines + footer)


def on_page_markdown(markdown: str, page, config, files):
    if page.file.src_path != WIRING_PAGE or MARKER not in markdown:
        return markdown

    yaml_path = Path(config["docs_dir"]) / YAML_REL
    try:
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:  # noqa: BLE001
        print(f"Warning: could not render wiring table from {yaml_path}: {e}")
        return markdown

    return markdown.replace(MARKER, render_table(data))
