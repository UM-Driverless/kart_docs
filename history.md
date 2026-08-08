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

---

## 2026-07-16 — tasks.md consolidated to the repo root; `.agents/tasks.md` retired

`.agents/tasks.md` was moved to `tasks.md` at the repo root with `git mv`, so the file's history follows it. `.agents/tasks.md` no longer exists in this repo and must not be recreated — the rule is one `tasks.md` per repo, at the root.

**Rationale:** tasks are the project's tasks regardless of who does them. Two files named `tasks.md` only produce duplicates and stale entries, because whichever one the current session isn't reading quietly goes out of date.

`AGENTS.md` previously didn't mention the task board at all; its "Key Files (Read Before Working)" list now names `tasks.md` first, ahead of `.agents/error-log.md` and `.agents/definition-of-done.md`.

Note: `docs/assembly/pneumatic-braking/index.md` points at `dv/tasks.md`, which is a *different* repo's board, not this one — it was already correct and was left alone. Stale `.agents/tasks.md` paths in append-only records (`history.md`, `.agents/error-log.md`) were also deliberately left as written: they were accurate on the date they were logged, and rewriting them would falsify the record.

---

## 2026-07-30 — `legacy-wiring.md` deleted: the ESP32-S3 Medulla PCB is the board in the kart

The classic-ESP32 page has been deleted, executing the plan recorded in the 2026-04-13 entry
above ("Delete `legacy-wiring.md` once the S3 PCB is manufactured, flashed, and deployed in
the kart"). Confirmed by Rubén: the ESP32-S3 interface PCB is installed and the hand-wired
classic ESP32 (ESP32-DevKitC V4, flying wires, no PCB) is out of the kart.

**Trigger.** Searching the live site for "esp32" returned "Legacy wiring (classic ESP32)" as
the *first* of 24 results, above every current page — so the top hit for the project's main
microcontroller was a retired pinout. The page carried a prominent "temporary page" warning
and was correctly nested in the nav, and that still wasn't enough: search surfaces pages
context-free, so a page that is only correct when read with its banner will be read wrong.
The lesson is that a legacy page's cost is paid at search time, not at nav time — retire it
on the day it stops being true rather than leaving it to be sorted out later.

**Removed.** `docs/assembly/electronics/kart-medulla/legacy-wiring.md` plus the five
classic-ESP32 images it was the only referent of (`esp32-devkitc-v4-pinout.png`,
`esp32-devkitc-v4-typec-header-pinout.png`, `ESP32-DevKitC-Dimensions.png`, and two that were
already orphaned: `ESP32-DOIT-DEV-KIT-v1-pinout-mischianti.png`, `ESP32-pinout-diagram.jpg`).
The nav entry under Kart Medulla is gone. The ESP32-S3 pinout on
`kart-medulla/index.md` was already complete and correct; nothing was migrated.

**Docs that still claimed the classic board was installed, now corrected.** The repo had been
inconsistent for a while — `wiring.md` and `kart-medulla/index.md` described the fabricated S3
board with its `CNx.y` terminals and physical board-rework steps, while `legacy-wiring.md`,
`bom.yaml`, and both BOM pages said the classic ESP32 was the operational setup:

- `bom.yaml` — `esp32_s3` `status: planned` → `active`; `esp32_wroom_32` description and notes
  rewritten as retired. Its `pin_assignments:` block was deleted — it held a *third*
  classic pinout that disagreed with the legacy page itself (it claimed GPIO 18/19 for the
  Orin UART and GPIO 25/26 for the motor driver) and no script read it.
- `esp32_wroom_32` keeps `status: legacy` rather than being deleted, per the 2026-06-14 QR
  convention: the row must stay resolvable so stickers on the physical modules don't 404.
- `docs/bom/index.md`, `docs/bom/full.md` — "currently hand-wired in the kart" → retired.
- `orin-setup.md` — the `esp32dev` flashing command is unchanged (it is still the image that
  gets flashed), but its comment no longer describes it as "the legacy hand-wired classic
  ESP32 currently in the kart", which is now false about the hardware.

**Stale DAC part name fixed in passing.** `docs/bom/full.md` still listed a planned "MCP4728
quad 12-bit I²C DAC", and `bom.yaml`'s `esp32_s3` entry referenced the MCP4728 twice. The
design switched to the **MCP4922** (dual 12-bit SPI) on 2026-04-17. The MCP4922 still has no
component entry of its own in `bom.yaml` — filed in `tasks.md`.

Verified with `mkdocs build --strict`: no broken links, and "Legacy wiring" no longer appears
in `site/search/search_index.json`.

---

## 2026-07-30 — Settled: the kart runs the `esp32-s3-devkitc-1` build, not `esp32dev`

The earlier entry today left an open contradiction: `firmware.md` said the board is an
ESP32-S3 while also calling the classic `esp32dev` environment "the image that actually runs
on the kart", and the `orin-setup.md` edit in that same commit repeated the claim. Both were
wrong. A classic-ESP32 image cannot run on an S3 at all — Xtensa LX6 vs LX7, and esptool
rejects the chip-ID mismatch — so this was never a question of which was more current, only
of which one was false.

**Checked directly on the kart's Orin over `orin-remote` (read-only, nothing stopped or
flashed):**

- `~/kart_medulla/.pio/build/` contains exactly one environment, `esp32-s3-devkitc-1`, with a
  `firmware.bin` from 2026-07-30 11:08. There is no `esp32dev` build directory at all.
- The ESP32 is on `/dev/ttyACM0`; no `/dev/ttyUSB*` exists on the machine. The classic board's
  CP2102 enumerated as `ttyUSB0`, so its absence is itself evidence.
- `lsusb` shows `1a86:55d3 QinHeng Electronics USB Single Serial` — the WCH CH343 on the S3
  board.

Corroborating, from session transcripts: two `pio run -e esp32-s3-devkitc-1 --target upload
--upload-port /dev/ttyACM0` runs over `ssh orin-remote` on 2026-07-26 both reported SUCCESS,
one of them immediately before a commit whose message quotes steering values "measured on the
kart". `platformio.ini` confirms `[env:esp32dev]` still has `board = esp32dev` — it was never
repointed at the S3; it is a fallback that is simply not used.

**Where the false claim came from.** `platformio.ini` still carries a comment above the S3 env
saying it "does NOT link yet", and `.agents/esp32s3-pinmap.md` still says "The S3 build does
not exist." Both were true when written and were never updated after the S3 target started
working. `firmware.md` faithfully copied them. The lesson is that a doc which cites its source
is only as fresh as that source — `firmware.md` even flagged "doc lag" in those two files
while trusting their substance.

**Fixed here:** `firmware.md` (warning block, env table, and flashing section rewritten around
the S3 target) and `orin-setup.md`. Two further errors surfaced while verifying the flashing
commands against the live machine: the repo path on the Orin is `~/kart_medulla` with an
underscore, not `~/kart-medulla`, and `pio` is **not** on the Orin's PATH (`which pio` returns
nothing) — it must be called as `~/.local/bin/pio`. The documented flash sequence would have
failed on both counts. It also now stops and restarts `kart-brain`, which holds the serial
port.

**Left open in `tasks.md`,** because they live in the `kart-medulla` repo: the three stale
statements above, and a real unresolved one — `AGENTS.md` says `km_gpio.h` uses the S3 pin map
while `.agents/esp32s3-pinmap.md` says it still holds the classic map. That one is
safety-relevant: under the classic map `PIN_STEER_PWM` is GPIO 18, which on the S3 board is
the gate of Q3, the shutdown-circuit MOSFET.

Also added the **MCP4922-E/SL** as its own `bom.yaml` component (it had none), with the
MCP4728 recorded under `rejected:`. Its unit cost is a placeholder — the chips came from
workshop stock and no price was paid.

---

## 2026-07-30 — Module standard changed: the fitted N16R8 is accepted, the "never R8" rule retired

The docs specified **ESP32-S3-WROOM-1-N8R2** and carried an explicit "DO NOT BUY" rule against
octal-PSRAM (R8) variants. The module actually on the board is an **N16R8** — an R8. So the
BOM banned the part it was describing, and the earlier edit today that flipped `esp32_s3` to
`status: active` made it worse by asserting the N8R2 was the installed part.

**Evidence the fitted module is R8:** `esptool` on the hardware reports `ESP32-S3 (QFN56)
revision v0.2` with `Embedded PSRAM 8MB (AP_3v3)` — 8 MB of PSRAM is octal, quad variants are
2 MB. Three independent statements in the firmware repo agree: `AGENTS.md` ("the kart-medulla
PCB now carries an ESP32-S3 (WROOM-1-N16R8)"), `.agents/error-log.md`, and
`.agents/esp32s3-pinmap.md` ("The fitted module is an **N16R8**").

**Decision (Rubén, 2026-07-30): accept the R8 and rewrite the rule.** The ban was written to
protect GPIO 33–37, but the pinout had already been changed to leave all five free — 33, 35,
36 and 37 are `HOLD`, `CMD_REVERSE` moved to the PCF8574 expander on 2026-05-03, and
`MOTOR_HALL_1` moved off GPIO 37 to GPIO 16. The thing the rule was protecting had already
been given up voluntarily, so the R8 costs this design nothing and the rule was the stale part.

The constraint that remains real, and is now stated that way: **GPIO 33–37 must never be
assigned.** Substituting a quad-PSRAM module (N16R2, N8R2) is a safe drop-in that *frees* those
pins; the failure case is the reverse — assigning 33–37 and then fitting an R8.

**Contradictions this cleared up, all pre-existing.** `index.md` had two adjacent admonitions
saying opposite things: a note headed "N8R2 preferred; N8R8 still works" immediately above a
danger block headed "octal-PSRAM variants (R8) are tolerated, never preferred" whose body then
said "**Do not substitute an R8 variant**" — tolerated and forbidden in the same breath. Both
are replaced by one block. `bom.yaml` separately claimed "**GPIO 33–37 are NOT reserved by our
pinout** ... the pinout may and does use GPIO 33–37 when needed", which the pin table on
`index.md` had contradicted since at least 2026-05-08 by marking all five `HOLD`. And
`index.md` still described `CMD_REVERSE` as living on GPIO 36 flagged `SPARE/CMD_REVERSE`,
two months after it moved to the PCF8574.

Also corrected while sweeping: `docs/bom/full.md` still listed the medulla PCB as "next
revision, blank" with its terminal blocks and level shifters as "Planned", though the board is
fabricated, populated, and running the kart; and `wiring.md` linked to the medulla page as
"Kart Medulla (ESP32)".

**Naming note for anyone reading old text:** "N8R8" appears in a few places in the pre-2026-07-30
docs where "N16R8" was meant. N8R8 is a real Espressif part (8 MB flash, 8 MB octal PSRAM), just
not the one on this board.

---

## 2026-07-30 — Pin table diffed against dv-hardware; U12 does not exist, the part is Q4

Following the module-suffix fix, the ESP32-S3 pin table was compared row-by-row against its
declared source of truth, `dv-hardware/projects/kart-medulla/docs/pinout-esp32-s3.md`. The
kart-docs table claimed to mirror it "as of 2026-05-08"; that file has since been edited twice
(2026-07-10 bench bring-up, 2026-07-18), so the claim was ~2.5 months stale.

**All 44 rows agree except two, and on those two kart-docs is the more current side.**
dv-hardware still lists GPIO 1 as `PRESSURE_3` and GPIO 3 as `BUZZER` in its `Signal` column
even though its own notes describe both reassignments. So the blanket "if the two disagree,
dv-hardware wins" rule would have *undone* the steering-angle-PWM and compressor-PWM
repurposings. The rule is now scoped: dv-hardware wins everywhere except those two rows, and
the underlying fix is filed in `tasks.md` as an upstream job.

**Corrections pulled down from the 2026-07-10 bench session:**

- **GPIO 3 is not a strap pin on this chip.** The old note said "Strap pin (JTAG src select),
  idle-high at boot is acceptable". Both halves were measured wrong: the `STRAP_JTAG_SEL` eFuse
  is unburned so GPIO 3 is never sampled at reset, and `IO_MUX_GPIO3 = 0x0a02` shows no
  internal pull, so it floats and an external pulldown wins at boot. That is precisely why it
  is safe driving the compressor MOSFET gate.
- **GPIO 35–37 are `BLOCKED`, not `HOLD`.** With an N16R8 fitted they are not reclaimable at
  all, so the status legend now separates "kept free by choice" from "physically impossible".

**U12 does not exist.** The docs described the REVERSE-wire driver as "U12, a PC357N1J000F
optocoupler, swapping to a BSS123 in the next schematic edit, board not yet manufactured, swap
is free". Every clause was wrong: the part is **Q4**, a BSS123, already fitted on a
manufactured and bench-tested board. The netlist's reference designators are
`U1, U02, U5, U13, U14, U19, U23, U24, U25` — no U12 anywhere in schematic, PCB, netlist or
BOM. The optocoupler was never placed on a sheet; it survives only as an unused library entry
in the EasyEDA source, and even the 2026-05-03 export already has the BSS123 placed as Q4.

**One conflict left open rather than guessed at.** kart-docs puts the reverse-command wire on
terminal **CN4.3**; the dv-hardware netlist puts `/REVERSE_WIRE` on **CN8 pin 1**, which
kart-docs assigns to `SDC_IN_LOW_SIDE`. Mixing up a reverse command with the shutdown-circuit
terminal is not a harmless error, and nothing on hand settles it — CN6–CN10 are already flagged
as possibly physically reversed. Both `index.md` and `wiring.yaml` now carry an explicit
"unverified" marker at that terminal, and it is filed in `tasks.md` for a check against the
board.

Verified after the edits: `check_wiring.py` still reports 115/115 connectable pins wired, and
`mkdocs build --strict` is clean.

---

## 2026-07-30 — CN4.3/CN8.1 settled: kart-docs was right, the dv-hardware netlist's CN numbers are not the silkscreen's

Confirmed by Rubén: on the board, **CN4.3 carries REVERSE and CN8.1 is `SDC_IN_LOW_SIDE`** —
exactly what `wiring.yaml` and `kart-medulla/index.md` already said. The "unverified" markers
added to both files earlier today have been removed.

The discrepancy that prompted them is real but lives upstream, and it is worse than a swapped
pair. `dv-hardware/projects/kart-medulla/output/netlist.net` (exported 2026-05-07) puts
`/REVERSE_WIRE` on **CN8 pin 1** *and* `/SDC_IN_LOW_SIDE` on **CN5**. Two nets, two different
mismatches — so the netlist's `CN` reference designators are simply not the silkscreen `CN`
numbers, rather than being off by a consistent permutation. The KiCad project is a ConvertEDA
import of the EasyEDA original, which is the likeliest point at which connector designators
were reassigned.

The consequence is worth stating plainly, because it is the kind of thing that gets someone
hurt: anyone wiring the kart from that netlist would land the **reverse command on the
shutdown-circuit terminal**. Filed in `tasks.md` — the netlist stays useful for nets and part
designators (it is how `Q4`/BSS123 was confirmed), but it is not authoritative for terminal
numbers until the designators are reconciled.

**Method note.** The mismatch surfaced only because the pin table was diffed against its
declared source of truth instead of being trusted, and it was resolved only by asking the one
person who could see the board. Neither half would have worked alone: the diff found the
conflict but had no way to say which side was right, and the netlist looked authoritative
precisely because it is machine-generated. Machine-generated does not mean correct about
physical labels — it means faithful to whatever the schematic's designators say, which is a
different claim.

---

## 2026-07-30 — `km_gpio.h` settled: both pin maps live behind a compile-time switch

The last open safety question is closed, and the alarming version of it was wrong.
`components/km_gpio/km_gpio.h` does not "hold the classic map" *or* "hold the S3 map" — it
holds **both**, selected by `#if defined(CONFIG_IDF_TARGET_ESP32S3)` with the classic map in
the `#else` branch. Building the `esp32-s3-devkitc-1` environment takes the S3 branch:

- `PIN_STEER_PWM` = GPIO 40
- `PIN_STEER_DIR` = GPIO 17
- `PIN_SDC_NOT_EMERGENCY` = GPIO 18
- `PIN_STEER_PWM_IN` = GPIO 1, commented `CN5.2 — MT6701 OUT, ~994 Hz PWM angle frame`

which matches the kart-docs pin table on every one of those pins, including the GPIO 1
repurposing that dv-hardware's own table has not caught up on.

So `AGENTS.md` was right and `.agents/esp32s3-pinmap.md` is stale. The hazard raised earlier
today — "under the classic map `PIN_STEER_PWM` is GPIO 18, which is Q3's gate" — is real about
the `#else` branch and irrelevant in practice, because that branch is not compiled for this
board. Worth recording as a false alarm rather than quietly dropping: the reasoning was sound
but rested on treating two docs' disagreement as evidence about the code, when the code was
readable the whole time and answered it in one grep.

Remaining stale statements in the firmware repo are consolidated into a single `tasks.md`
entry, now including `km_gpio.h:108`, whose `#else` branch is still labelled "(current build)".

---

## 2026-07-30 — Audited the docs nobody had opened: software, mechanical, rules, top-level

The electronics sweep earlier today only covered `docs/assembly/electronics/**` and
`docs/bom/**`. Three parallel audits covered the rest, and their claims were then checked
against two authorities rather than taken on trust: the `kart-brain` ROS 2 source, and the live
Orin.

**Two facts settled by looking at the running machine.** `/dev/serial/by-id/` on the Orin holds
exactly one entry, `usb-1a86_USB_Single_Serial_5C37207028-if00 → ttyACM0`, which matches the
`serial_port` default in `kb_coms_micro.cpp:6` — so the docs' Silicon Labs CP2102 path was
stale on both counts (wrong vendor, and the real default is a `by-id` path rather than a bare
device node). And `ss -tlnp` shows the dashboard process listening on **port 80**, confirming
`dashboard.md` and refuting the three pages that said 8080.

**The most consequential fix was a latency figure that inverted a conclusion.**
`performance.md` documented the ESP32 PID loop at 10 Hz / ~100 ms and drew the reasonable
conclusion that the microcontroller was the pipeline's largest tail after perception. The
firmware's actual control task targets 500 Hz (2 ms). `firmware.md` had already flagged 10 Hz
as a superseded number months ago; `performance.md` was the surviving copy. Fixing the number
also required rewriting the surrounding prose, the pipeline budget diagram, and a measurement
checklist item that asked whether "the 10 Hz PID cycle" was stable — a stale number does not
sit in one cell, it grows conclusions around itself.

**Corrections applied.** `/dev/ttyUSB0` → `/dev/ttyACM0`; CP2102 → the real WCH by-id path;
port 8080 → 80 in three places; `cmd_vel_bridge` documented as subscribing `/kart/cmd_vel`
when the source says `/kart/cmd_vel_muxed` (the wrong version implied the state-machine safety
mux was bypassed); `zed2i` → `zed2`; YOLOv11s at 640 px → YOLOv11n at 320; `/esp32/health` →
the real `/esp32/health/flags` + `/esp32/health/data`; `/esp32/throttle` marked as
simulator-only, since on hardware `kb_coms_micro` publishes `/esp32/acceleration` and that
dashboard dial stays blank; `ros2 launch kb_dashboard dashboard.launch.py` → `kart_bringup`
(both packages have a file by that name, and they are not equivalent); and
`state_machine.md`'s claim that the gamepad publishes `/kart/cmd_vel_manual` — it publishes
`/kart/cmd_vel`, the *autonomous* input, which is worth knowing before trusting the mux.

Outside software: `faq.md` argued the Orin's 40-pin header could replace the ESP32 because it
has "2 hardware PWM channels (steering servo + motor ESC)". There is no ESC and throttle is not
PWM — it is an analog DAC output — so the trade-off was mis-scoped, not merely mislabelled.
`index.md` was dated `2025-06-18`, ten months before the kart existed, and both it and
`about.md` still said steering actuation was "ordered" three weeks after the kart drove itself.
`assembly/index.md` described the MCU as "ESP32, UART 115200" and throttle as "0–3.3 V (66% max
until 5V DAC available)" — a limitation the fitted MCP4922 removed. The CAN diagram on
`steering/index.md` and the CAN transceiver line on `computer.md` both contradicted "no CAN
anywhere on the kart"; the transceiver is real but unused, so that line now says so.
`as_state_machine.md` described the dashboard stop button as equivalent to ASMS-off when it
returns to `AS_READY` and stays armed.

Also: `docs/rules/` was reachable only by an inline link and is now in the nav; the orphaned
`assembly/electronics/microcontroller/` directory (a Blue Pill page and two pinout images from
before the medulla existed, referenced by nothing) was deleted; and the build-journey's
"every Wednesday" claim was softened, since 5 of 13 posts landed on a Wednesday.

**Left open in `tasks.md`, four items that need a person or a multimeter:** what actually powers
the Cytron H-bridge (two pages say the 12 V rail, `steering/index.md` says the 48 V pack and
specs stall at 47 V × 43 A); rewriting the camera page's YOLOv5 export walkthrough for v11;
whether the kart is presented as a competition entry (`index.md` says it will not compete,
`as_state_machine.md` calls it an APC entry and tracks rule compliance); and reconciling three
different mission lists — during which the audit turned up a live bug worth repeating here:
`throttle_test` is gated as an autonomous mission but is missing from `protocol.py`'s
`MISSIONS` map, so `MISSIONS.get(..., 0)` sends it to the ESP32 as **manual**.

---

## 2026-07-30 — The Cytron runs off the 48 V pack; the 12 V claim was wrong in three files

Settled by Rubén: the steering H-bridge is fed from the **48 V traction pack**, not the 12 V
rail. So `steering/index.md` — the page flagged as the outlier when the audit found this — was
the correct one, and the two pages that agreed with each other were both wrong. Worth
remembering: two sources agreeing is not evidence, when one was written by copying the other.

Corrected `kart-medulla/index.md` (the 2026-05-01 decision entry) and
`electronics/power/battery.md` (which listed the H-bridge among the 12 V rail's loads). In
`wiring/wiring.yaml` the Cytron's supply pin moved from the `12V` net to `PACK48` and was
renamed `v12` → `vin` — the old pin name encoded the wrong answer, so leaving it would have
re-seeded the error — and `STEER_M+` / `STEER_M-` are re-labelled 48 V. `check_wiring.py` still
reports 115/115 pins wired.

The Cytron MD25HV takes 7–58 V, so the pack is within spec, which is why nothing downstream
needs to change. The "powered permanently, not switched through the manual/autonomous mode
switch" half of the original decision is unaffected: that was about inrush current browning out
the Orin on every switch into autonomous, which is a question of *when* it is connected, not of
*which rail*. Only the rail was wrong.

---

## 2026-07-31 — Part IDs are per-design, not per-physical-unit (amends 2026-06-14)

**Decision.** A part ID (`part_id`, the 16-digit number in the QR) identifies a **design revision**,
not an individual physical object. Every board built to the same revision carries the same sticker
and resolves to the same `/p/<id>/` page. Ruben's call, 2026-07-31.

**What this changes.** The 2026-06-14 entry above ("QR scan resolves to the BOM") wrote "a QR carries
a per-physical-unit opaque ID". That wording is superseded. Its *reasoning* is untouched and in fact
argues for per-design: the motivating case is telling apart versions that look physically identical
(Orin adapter v1 vs v2, ESP32-WROOM-32 vs ESP32-S3), and a per-design ID separates those completely.
Per-unit IDs would only add distinguishing two boards of the same revision from each other, which
nothing in the project needs, at the cost of a unique sticker and a unique page per object built.

Everything else in that entry stands: the QR holds only the opaque ID, resolution is relative through
`/p/<id>/`, superseded revisions get `status: legacy` rather than deletion so old stickers still
resolve, and a `/p/` page is deleted only when the part and its stickers are gone.

**Vocabulary, so the two levels have real names.** The design-level number is a **part number** (PN;
**MPN** when it is the manufacturer's own, **GTIN** in the GS1 barcode world). A per-object number is a
**serial number** (SN; **UII** under MIL-STD-130's IUID scheme, **SGTIN** in GS1/EPC). This project has
the first and not the second. If per-object tracking is ever needed, add a `serial` field alongside
`part_id` rather than redefining `part_id` — PN plus SN on one label is the standard form, and it
extends the scheme without invalidating a single printed sticker.

**Consequence for revisions.** Each revision needs its own part ID and its own page, since the ID *is*
the revision. Created the same day: `Kart Medulla PCB v2` = `1604 0948 4608 5574`
(`docs/p/1604094846085574.md`).

**Addendum (same day) — the names we use.** The standard names read backwards to us ("part number"
sounds like it names the object; "serial" sounds like it must count up, and modern ones often do not),
so the project uses plain names, with the standard ones kept as the translation for suppliers:

| Level | Our name | Standard name |
|---|---|---|
| The design revision — every unit built to it shares this | **design ID** | **PN**, part number (**MPN** when it is the manufacturer's own) |
| One individual physical object | **unit ID** | **SN**, serial number |

The 16-digit number in the QR is a design ID. There is no unit ID in the system, and adding one would
mean a second field, not a redefinition of the first. Use PN/MPN when talking to suppliers — that is
the term they answer to. The `part_id` field name is unchanged for now; renaming it to `design_id`
would touch `scripts/new_part.py`, `docs/scan.md`, `docs/p/index.md` and the frontmatter of each
existing part page.

**Not UII.** MIL-STD-130's unique item identifier was considered as a name for the unit ID and
rejected: a UII is not a bare number but a concatenation of issuing agency code + enterprise
identifier (CAGE/DUNS/DoDAAC) + serial (Construct 1), or the same with the part number inserted and
the serial only unique within it (Construct 2). It presumes a registered enterprise, and the standard
also specifies the mark as Data Matrix ECC 200 with a defined data syntax rather than a QR carrying
bare digits. The serial component itself may be random — nothing in the standard requires counting up
— but that does not make a random number a UII. SN stays the standard equivalent of unit ID.

## 2026-08-08 — CN1–CN10 pinout published, and cross-repo links pinned to commits

The medulla connector table was never missing, just invisible from here: it lives in dv-hardware as
`projects/kart-medulla/docs/pinout-cn-connectors.md`, next to the KiCad schematic that defines it,
and this repo only linked at it in prose. `scripts/sync_pinout.py` now copies it verbatim into
`docs/assembly/electronics/kart-medulla/pinout.md` under a provenance banner. Still one authored
table, so the drift that got the old hand-maintained tables deleted cannot return.

The copy is committed rather than rendered by a mkdocs hook the way the wiring and BOM tables are,
because GitHub Actions checks out kart-docs alone and cannot reach dv-hardware at build time.
`--check` reports staleness wherever the source is visible and exits 0 where it is not.

**Cross-repo links are pinned to a commit, never `main`** (Ruben's rule, this session): a `main`
link silently changes meaning as the other repo moves, so a reader comparing the copy against
"the source" would be reading a different document than the one that produced it. The banner
carries a permalink to the exact revision plus its date; syncing from a dirty dv-hardware working
tree is refused, because such a copy would correspond to no commit. `--allow-dirty` overrides.
`pinout-esp32-s3.md` and `esp32-s3-pin-capabilities.md` links in the medulla page are pinned too;
dv-hardware's `projects/kart-medulla/README.md` is deliberately left on `main`, because it is a
living rework list that is meant to be read as current state.

Three things found while doing it:

- **Every `dv-hardware` link in this repo pointed at `github.com/rubenayla/dv-hardware`, which
  404s.** The remote is `UM-Driverless/dv-hardware`. All of them were dead; all are fixed.
- Two stale pointers on the medulla page: it told readers to filter the wire list's `From`/`To`
  columns (the column is `Connected pins`, and pins read `medulla.CN1.2`), and claimed the
  "ESP32-S3 Pin Assignment" section above held a table with a `Silkscreen` column — that section
  explicitly carries no table.
- kart-docs and kart-medulla disagreed on the CN5.2 rework. This repo said remove R10 only; the
  firmware repo said R9+R10. Ruben confirmed this repo was right, and kart-medulla was corrected
  (`078e34e` there). kart-medulla also still called the steering sensor an AS5600.

kart-medulla reads dv-hardware directly rather than going through kart-docs: it is a peer of the
hardware repo, and a hop through the docs site could only ever be staler than what it reads today.
