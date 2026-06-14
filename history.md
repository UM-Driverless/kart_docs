<!-- consult selectively — grep, never read in full -->

# History

Append-only log of notable decisions and events for `kart-docs`. Chronological (oldest first), append at the end.

---

## 2026-04-13 — Kart Medulla MCU: classic ESP32 → ESP32-S3 (docs reframed)

**Decision.** The next revision of the Kart Medulla interface PCB targets the **ESP32-S3** (ESP32-S3-WROOM-1 module). The classic ESP32 (ESP32-WROOM-32 on a DevKitC V4) is retired as the target MCU for new hardware.

**Status at decision time.** No Kart Medulla PCB has been manufactured. The classic ESP32 is currently hand-wired directly in the kart for basic functionality — this continues to be the operational setup until the S3 PCB is built and flashed.

**Why.**

- **Pin count.** The classic ESP32 ran out of usable GPIOs once CAN, SPI, status RGB, buzzer, and the Orin link were added on top of 3× halls, 3× pressure, accelerator, brake, SDC, steering, and relay. Too many classic-ESP32 GPIOs are reserved for flash/SDIO or are strap-pin traps. The S3 offers ~45 usable GPIOs.
- **Native USB-OTG.** Orin link moves from UART (through an external USB-UART bridge chip) to direct USB CDC-ACM — drops a BOM item, raises throughput from ~1 Mbit/s to ~12 Mbit/s full-speed USB, and gives hot-plug handling for free.
- **Built-in USB-Serial-JTAG.** Flash + serial monitor + step-debugging over one USB cable. No external ESP-Prog / FT2232H.

**Trade-off accepted.** The S3 has no built-in DAC, so `CMD_ACC` (5V analog throttle output) now comes from an external **MCP4728** (quad 12-bit I²C DAC) on the interface PCB. 12-bit vs the classic's 8-bit is a resolution upgrade. MCP4728 shares the existing I²C bus, so no additional GPIO cost.

**Variants considered and rejected.** ESP32-S2 (has DAC but single-core, no BT), ESP32-C3 (too few GPIOs), ESP32-C6 (no DAC, Wi-Fi 6 unnecessary for a kart), ESP32-H2 (no Wi-Fi).

**Docs reframe performed today.**

- `docs/assembly/electronics/kart-medulla/index.md` — rewritten around ESP32-S3 (new pinout table, hardware decisions, Why-S3 rationale).
- `docs/assembly/electronics/kart-medulla/legacy-wiring.md` — new page preserving the classic ESP32 hand-wiring as currently deployed in the kart. **Temporary** — to be removed once the S3 PCB is deployed.
- `mkdocs.yml` — nav renamed "Kart Medulla (ESP32)" → "Kart Medulla (ESP32-S3)" with the legacy page nested under it.
- `docs/assembly/electronics/bom.yaml` — added `esp32_s3` entry (status `planned`); `esp32_wroom_32` demoted to `status: legacy` with a pointer to the legacy wiring page.
- `docs/bom/index.md` — now lists both MCUs.
- `docs/assembly/electronics/orin-setup.md` — PlatformIO flashing snippet now shows both environments (`esp32dev` for the legacy setup, `esp32-s3-devkitc-1` for when firmware migrates).

**Pointers to deeper context.**

- PCB project + `.epro` backups + full decision log: Drive folder `formula_24-25-26/dv/kart/kart-medulla/` — especially `README.md`, `history.md`, and `pinout-esp32-s3.txt` (which keeps both classic and S3 pinouts side-by-side as a reference).
- EasyEDA project: account `dv.umotorsport@gmail.com`, Personal Workspace, project ID `5b30b0a2e25c44179a5af8629b1dff0d`.

**Follow-ups.**

- Firmware (`kart-medulla` repo) needs to gain a working `esp32-s3-devkitc-1` PlatformIO/IDF configuration. `sdkconfig.esp32-s3-devkitc-1` is already present; pinout in firmware will need updating to match the S3 assignments once they're finalized during PCB layout.
- Delete `legacy-wiring.md` once the S3 PCB is manufactured, flashed, and deployed in the kart.

---

## 2026-04-23 — ESP32-S3-WROOM-1 suffix locked: N8R2 (R8 banned)

**Decision.** The exact module to order is **ESP32-S3-WROOM-1-N8R2** (8 MB flash, 2 MB quad PSRAM). Any octal-PSRAM variant (R8) is **banned** for the Kart Medulla.

**N8 vs N16 (flash).** The `N` suffix is on-module QSPI NOR flash. Flash size does not affect pinout — it all lives on the internal QSPI bus. N8 (8 MB) is plenty for this firmware (code < 1 MB, room for dual OTA slots + filesystem + growth). N16 (16 MB) is a silent upgrade path if ever needed.

**R2 vs R8 (PSRAM) — this is the critical one, and it is PHYSICAL, not firmware-configurable.**

- **R2 = 2 MB quad PSRAM.** Shares the existing QSPI flash data lines inside the module. Costs zero additional module pins. All GPIOs remain available.
- **R8 = 8 MB octal PSRAM.** The octal PSRAM die is hard-wired inside the module package to **GPIO 33–37** (the SPI0/1 extension pins). Espressif's ESP32-S3-WROOM-1 datasheet explicitly marks GPIO 33–37 as **not available** on R8 variants. Those module pads exist on the footprint but are permanently tied to PSRAM data lines inside the package.

**Why you cannot "just ignore PSRAM" on an R8 module.** Disabling PSRAM in `sdkconfig` does NOT reclaim GPIO 33–37. The PSRAM die is physically attached to the traces inside the module regardless of firmware. Driving those pads externally risks contention with whatever the PSRAM does at power-up (the ROM bootloader probes PSRAM). Treating an R8 board as if it were an R2 board is a hardware-level error, not a firmware choice.

**Rule (crystal clear).** For the Kart Medulla, only quad-PSRAM WROOM-1 variants (R2, or no PSRAM) are acceptable. R8 is rejected. This applies to the ordered module AND to any dev-board purchase — an ESP32-S3-DevKitC-1 with an N16R8 module soldered on is not a drop-in substitute for the N8R2 variant.

**GPIO 33–37 policy.** Our pinout does NOT treat GPIO 33–37 as reserved. We will try to leave them free where it is convenient, but that is a courtesy, not a commitment, and it is NOT the standard we follow. The module must make those pins available — i.e., the module must never be R8. If a future revision ever wanted to move to R8, the pinout would first have to be audited to confirm GPIO 33–37 are genuinely unused, and that audit has NOT been performed and is NOT planned.

**Alternatives on file.**

- **ESP32-S3-WROOM-1-N16R2** — valid upgrade path if firmware ever outgrows 8 MB flash. Quad PSRAM, zero GPIO cost, no PCB/pinout change required. This is the proper "fallback with headroom," replacing the previous mention of N16R8.
- **ESP32-S3-WROOM-1-N16R8** — **DISCARDED.** See above.

**Action.** Buy ESP32-S3-WROOM-1-N8R2. `bom.yaml`, `kart-medulla/index.md`, and `docs/bom/index.md` updated accordingly.

---

## 2026-04-27 — Public BOM page + steering power budget; Festo prices redacted under V2 sponsorship

**What was done.**

- New `docs/bom/full.md`: shareable consolidated BOM with two cost columns (team cost vs market cost), `Source` column (Donated / Sponsored / Purchased / Salvage / Custom), per-section tables (chassis, powertrain, steering, electronics compute & control, electronics power, sensors, EBS, wiring & misc), totals, and a tooling section sized for a "what would a new team need" view.
- New `docs/assembly/steering/power-budget.md`: back-of-envelope steering torque/power calc (μ·N·a → ~15–20 Nm static at the steering shaft, ≥100 rpm for 0.3 s lock-to-lock, ~50 W cont / ~200 W peak operating; ~2 kW stall headroom available with the current setup, rarely if ever hit). Includes a "current setup (kept)" section and an "interesting alternatives (not currently planned)" table covering Bosch F006-B20 generic wiper, Bosch WDD2 motorsport actuator, Doga 319H with Hall feedback, Doga 319.4860, generic 24V planetary gearmotor.
- `mkdocs.yml`: BOM nav split into two pages (overview + full); steering nav adds Power Budget.

**Festo / EBS pricing — what changed and why.**

The first draft of `bom/full.md` carried catalogue ballpark prices for the Festo-supplied EBS components. After re-reading the **V2 sponsorship contract** (`marketing/sponsors/festo/convenio-festo-umotorsport-2026-v2-rev-busquets-18-03-26.docx`, Busquets review 2026-03-18), the per-line Festo prices were **stripped from the public page** and replaced with `redacted` markers. V2 added:

- **NOVENA — Confidentiality.** All information accessed in the course of the agreement, 5 years post-termination, breach is "incumplimiento grave."
- **OCTAVA — IP/trademark.** Limited, revocable license to use Festo brand under their guidelines; 7-day brand removal post-termination.
- **DÉCIMA — Liability.** Festo disclaims liability; team indemnifies Festo against third-party claims.
- **UNDÉCIMA — Jurisdiction:** Barcelona (was Madrid in V1).
- **EXPONEN III** clarified the relationship as "patrocinio publicitario mediante aportaciones no dinerarias y acciones de visibilidad."
- **SEGUNDA** new bullet: supply subject to availability; no obligation of continuous/exclusive supply.

Cap on Festo's seasonal supply is **€1 500 incl. VAT per season** (Cláusula SEGUNDA-1). The team's reciprocal obligations (Cláusula TERCERA): logo on the kart, IG/LinkedIn tagging, Formula Student event invitations, sponsor listing on the team website. Term to 2026-12-31.

V2 was returned by Festo on 2026-03-18 and was being sealed by Cristina (URJC marketing). Per Jorge's chat, as of late April the signed version had not been finalised, but the redaction posture is the same either way.

**Price-research ledger kept in Drive.** Public-distributor price research (15 of 18 items priced from IAS Components, esd.equipment, Direct Pneumatics, Motion World; 3 still `?`) is preserved at `formula/formula_24-25-26/dv/kart/pneumatics/festo-public-distributor-prices-2026-04.md`. If Festo later confirms in writing that retail-equivalent estimates are publishable, the numbers can be moved straight back into the public BOM without re-research.

**Other notable BOM facts captured.**

- Orin: Silicon Highway 2023-04 invoice — net €1 821.29 + €36 shipping = **€1 857.29 transferred**, intra-EU reverse charge (0 % VAT on invoice). True project cost ~€2 247 once URJC self-accounts the 21 % reverse-charge VAT (URJC has limited input-VAT deduction as a public university). Footnote on the row explains.
- Steering: salvaged 24 V geared DC motor from a discarded massage chair, run at 12 V, through a **15 : 1** 3D-printed planetary; AS5600 angle sensor on the shaft. Bench-measured ~2 kW stall capacity; normal operation 50–200 W. Off-the-shelf wiper motors don't replace it without an equivalent reduction stage and procurement is the limiting factor for the team.
- Battery cells: 60× Molicel P42A bought from NKON for €230 (€3.83/cell), 52 in the 13S4P pack → €198. No 12 V auxiliary battery — 12 V rail comes from a buck regulator off the 48 V pack. Pack assembled by team; nickel strip + Kapton + 3D-printed PETG enclosure + fire-retardant foam liner.
- Orin storage: 500 GB M.2 NVMe pulled from a personal laptop during a 2 TB upgrade. €0 to project. Big improvement on `apt`/builds/repos; no effect on autonomy runtime FPS.

**Team-cost result.** ~€3 095 transferred to suppliers, ~€3 485 including the ~€390 reverse-charge VAT on the Orin. Page-level *market* total is redacted (the EBS row pulls the sum into non-disclosable territory); a non-Festo retail subtotal of ~€4 815 incl. VAT is shown as a partial reference.

**Open follow-ups (not closed in this session).** Sponsors page on the public site to satisfy Cláusula TERCERA-4; pneumatic schematic on the EBS page; rechecking the BOM once V2 is signed and we have the green/red on what's publishable.

---

## 2026-05-04 — drawio vs hand-crafted SVG for the wiring diagram

After thrashing through five attempts at `wiring-global` (drawio auto-routed,
hand SVG, drawio + manual waypoints, D2/ELK, drawio + electrical stencils),
the team's preference was clear: real component photos and pixel-precise
layout matter more than tool ergonomics. The fifth iteration on `wip/wiring-svg-rich`
went with hand-crafted SVG and produced a usable result on the first pass.
Notes from that experience for the next person:

**drawio strengths.** CI export is wired up (`rlespinasse/drawio-export`).
GUI editing exists for someone who prefers drag-drop. Built-in electrical
stencil library has shapes for battery, motor, switches, op-amp, relay
(actual stencil names live in `mxgraph.electrical.miscellaneous.*`,
`mxgraph.electrical.electro-mechanical.*`, etc. — extract them with
`strings /Applications/draw.io.app/Contents/Resources/app.asar | grep mxgraph.electrical`
because the names are not all guessable; the wrong path renders as a fallback
rectangle silently).

**drawio weaknesses (encountered, not theoretical).**
- Auto-routing produces spaghetti the moment edges have non-trivial geometry.
- `verticalLabelPosition=bottom` on a stencil makes the label overflow the
  cell's geometry box, so neighbors that were at the original spacing now
  collide with the label of the cell above them. The fix is either to
  re-space everything (cascading shifts because the relay block has
  internal sub-elements) or to use horizontal label position (which then
  fights with the cell width). Both routes burned an iteration.
- Photo embeds via `shape=image;image=<path>` work in CI but the path
  resolution is fiddly — relative paths to images outside the diagram's
  directory frequently render as broken-image placeholders in the CLI
  export. Data URIs work but blow up the file size.
- Edges connect by source/target cell IDs, so when you reposition a
  component the edges follow — but their waypoints don't, so the
  routing degrades silently.

**hand-crafted SVG strengths (encountered).**
- Pixel-precise placement: `<rect x= y= width= height=>` and `<polyline
  points="...">` go where you tell them. No layout engine to fight.
- `<image href="../../../emergency-braking/images/components/festo-*.png">`
  resolves correctly in any browser-based renderer (Chrome headless,
  the deployed mkdocs site, the `<object>` tag in the markdown).
  ImageMagick can't resolve those, but you don't need ImageMagick if you
  render with Chrome headless.
- Component icons drawn as inline `<path>` / `<circle>` / `<rect>` are
  free — the 13-cell battery stack, the BLDC motor rotor with U/V/W
  terminals, the SDC relay coil + NO contacts, the kill mushrooms, etc.
  Took maybe 30 minutes of careful coordinate math, no library lookup.
- White-halo edge labels (`paint-order: stroke fill; stroke: white;
  stroke-width: 4px`) just work, no fighting drawio's label background.

**hand-crafted SVG weaknesses.**
- No GUI for non-coders. The team can edit but only via text.
- Moving one component does NOT auto-reroute its edges; you have to
  update the polyline points manually. For 30+ edges this is real work.
- Verifying overlaps requires render-and-look (Chrome headless screenshot
  + Read tool); there's no equivalent of drawio's "click and drag, watch
  it snap to a clean route".

**Rendering pipeline gotcha.** ImageMagick's SVG renderer (and `qlmanage`)
do NOT load `<image>` tags via relative file paths. Render previews with:
```
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --headless \
  --disable-gpu --screenshot=/tmp/r.png --window-size=2400,1800 \
  --hide-scrollbars --force-device-scale-factor=2 \
  "file://$PWD/docs/assembly/electronics/wiring/images/wiring-global.svg"
```
The deployed mkdocs site uses real browser SVG rendering, so what you see
in Chrome locally matches what the team will see on `um-driverless.github.io`.

**Branches left for comparison (none merged to main).**
- `wip/wiring-d2-rewrite` — D2 + ELK auto-layout. Cleanest edges of any
  attempt, but every component is a generic colored rectangle.
- `wip/wiring-drawio-rich` — drawio with electrical stencils for battery,
  motor, kill switches, KEY, impact, op-amp. Acronym legend added,
  Buck/brake-bullet text corrected. Has the label-overflow / overlap
  problems that pushed us off drawio.
- `wip/wiring-svg-rich` — the hand-crafted SVG. Real Festo photos,
  schematic-style component icons, pixel-precise layout. Current
  best candidate but not yet team-reviewed.

**Bottom line.** For a documentation-grade wiring diagram with hardware-
recognizable shapes that the team isn't going to drag around in a GUI
every week, hand-crafted SVG produced a better result faster than the
drawio iterations did. drawio remains the right call for diagrams the
team WILL drag around (because the GUI saves time over coordinate math),
but those diagrams should accept the visual constraint of "labeled
rectangles with auto-routed edges" rather than fighting for stencils
and embedded photos.

---

## 2026-06-14 — BOM stays YAML-in-git, kept separate from the Notion AI Inventory (linked, not merged)

**Decision.** The published BOM stays as the `bom.yaml`-in-git system that `generate_bom_hook.py` renders into the searchable parts table. It is not folded into the team's Notion "AI Inventory" database, and it is not replaced by a public filtered view of that database.

**Context.** The Notion AI Inventory is the team's most-used tool — it tracks physical stock (tools, bolts, components) by quantity and location. It overlaps the kart, so the question came up: merge the BOM into it (a `location: kart` value), or publish a filtered Notion view as the BOM, or leave the BOM as-is.

**Why separate-but-linked is the answer.** A BOM and an inventory answer different questions and are *different sets*, not the same set filtered:

- Inventory = "what physical stock do we own, how much, where is it now" — instance/quantity-level, location-tracked.
- BOM = "what does the kart design call for" — type-level spec, by assembly, with required quantities.
- The BOM has rows with **no inventory entry**: assemblies/sub-assemblies, custom-fabricated parts (Orin adapter, Kart Medulla PCB), and design-required quantities that are a spec rather than physical stock. The inventory has rows with **no BOM line**: tools, consumables, spares. The overlap is only the COTS purchased parts.

So a "filtered inventory view" can only ever be that purchased-parts subset dressed as the whole BOM. Two pain points the user raised are the same modelling error from opposite sides: "2 bolts in the kart, the rest on a shelf — how to display" is only ugly if you model physical *units* as rows (you want one part row with quantity-by-location, not 50 rows); "two formats are hard to copy-paste on transfer" only exists if the item lives in two places.

**Publish-surface reasons to keep the docs table:** it sits inside MkDocs in-site search, it feeds `llms.txt`/`llms-full.txt` for AI ingestion, it's themed, it works offline, and it carries no dependency on a Notion page staying public. An embedded public-Notion view loses all of those.

**Link mechanism instead of merge.** Give each inventory item an optional shared part ID (`bom_id`) and each BOM part the catalog ID, so inventory↔BOM cross-reference rather than getting copy-pasted. If freshness on the overlapping purchased rows ever becomes a real problem, add a one-way Notion→`bom.yaml` pull for just those IDs — never two-way sync.

**Tipping condition that would flip this.** If the published BOM ever becomes just "the list of components we bought" — purchased COTS only, no assembly hierarchy, no custom parts, and no `llms.txt` need — then the BOM *is* the purchased-parts subset of inventory and a public filtered Notion view becomes the lower-effort, always-fresh choice.

**State found today (drives the follow-up work).**

- **Data is stale.** 6 of 8 `bom.yaml` files untouched since 2025-09 (only `electronics` 2026-05, `steering` 2025-11). Placeholder/unverified data present: `powertrain/bom.yaml` motor lists Amazon ASIN `B0C6WXYZ` (fake) as `verified: true`; several `TBD`/`pending` part numbers and round-number costs.
- **Render looks bad.** `generate_bom_hook.py` emits hand-rolled inline-styled HTML (hardcoded `background:#f5f5f5`, white-text status badges, fixed colors). It bypasses the Material theme, so there is no dark-mode support and it clashes with the rest of the site.

**Follow-up (not yet done).** (1) Audit each `bom.yaml` against the real kart and `~/dv/kart/<subsystem>/` notes — fix fake/placeholder part numbers, costs, and status flags. (2) Rework the hook's output to use Material-friendly, theme-aware markup (dark-mode safe) instead of inline styles.

**Update (same day): the styling rework (2) is done.** `docs/stylesheets/bom.css` (new) holds all table styling on Material CSS custom properties (theme-primary header, soft status/criticality badges, dark-mode ready); `generate_bom_hook.py` now emits class-based markup with no inline styles and the filter/sort JS was tidied; `mkdocs.yml` wires `extra_css`. Verified by building + screenshotting. The data audit (1) is still open.

## 2026-06-14 — QR scan resolves to the BOM (kart-docs), not the Notion inventory

**Decision.** The part-label QR system (`/scan/` → `/p/<id>/`) is for **kart parts**, and a scan resolves to that part's **BOM component / engineering docs in kart-docs**, not to the Notion AI Inventory. An inventory link stays optional/secondary on the `/p/` page.

**Why.** The motivating use case is disambiguating **versions that look physically identical** (e.g. Orin adapter v1 vs v2, ESP32-WROOM-32 *legacy* vs ESP32-S3). A QR carries a per-physical-unit opaque ID, so look-alike units get different IDs → different `/p/<id>/` pages → each links to *its* BOM component, which already encodes the revision (`status`, per-version description). The Notion inventory counts stock by *type* and can't say which revision is the one mounted, so it's the wrong primary target here.

**Permanence rule preserved.** The QR holds only the opaque ID; resolution is relative through kart-docs `/p/<id>/`. Labels never encode a Notion URL (long, org-bound → perishable sticker).

**Requirement this imposes.** For disambiguation to actually work, BOM component IDs must separate versions (`orin_adapter_v1` / `orin_adapter_v2`), not collapse to a generic `orin_adapter`.

**Obsolete versions.** Mark the superseded BOM component `status: legacy` (renders as the grey "Legacy" badge) rather than deleting it — keeps the row visible-but-retired and lets an old sticker still resolve. Delete a `/p/<id>/` page only when the physical part *and* its sticker are gone; otherwise a scan would 404. Where a unit is retired in place, point its `/p/` page at the superseding component.
